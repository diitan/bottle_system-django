from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Order
from datetime import datetime
from django.utils.dateparse import parse_date

def _parse_delivery_date(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None, ""

    # Ưu tiên ISO: YYYY-MM-DD (input type="date" gửi lên dạng này)
    d = parse_date(raw)
    if d:
        return d, d.strftime("%d-%m-%Y")

    # Fallback nếu bạn đổi input sang dd/mm/yyyy hoặc dd-mm-yyyy
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            d = datetime.strptime(raw, fmt).date()
            return d, d.strftime("%d-%m-%Y")
        except ValueError:
            pass

    return None, raw  # fallback: hiển thị nguyên chuỗi

def _format_vnd(amount: int) -> str:
    try:
        amount = int(amount)
    except Exception:
        amount = 0
    return f"{amount:,}".replace(",", ".") + " VNĐ"

def parse_and_format_date(date_str: str):
    # input từ <input type="date"> là YYYY-MM-DD
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return d, d.strftime("%d-%m-%Y")
    except Exception:
        return None, date_str

#==========================================================
def order_form(request):
    # form data để hiển thị lại khi sửa
    pending = request.session.get("pending_order") or {}
    form_data = pending.get("form", pending)

    ctx = {
        'form': form_data,
        'data': form_data,
        'show_confirm': False,
        'show_paid': False,
        'show_pay': False,
    }

    if request.method == 'POST':
        stage = request.POST.get('stage', 'preview')

        if stage == 'preview':
            errors = []

            # 1) Lấy các field text
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            birth_year = request.POST.get('birth_year', '').strip()
            address = request.POST.get('address', '').strip()
            delivery_raw = request.POST.get('delivery_date', '').strip()

            # 2) Parse qty an toàn + validate 0..10
            def parse_qty(raw, label):
                try:
                    q = int(raw or 0)
                except Exception:
                    q = 0

                if q < 0:
                    errors.append(f"{label} không được âm.")
                if q > 10:
                    errors.append("Số chai vượt quá phạm vi của hệ thống. Vui lòng nhập số chai dưới 10.")
                return q

            qty_low = parse_qty(request.POST.get('qty_low', '0'), "Số chai thấp")
            qty_mid = parse_qty(request.POST.get('qty_mid', '0'), "Số chai trung")
            qty_high = parse_qty(request.POST.get('qty_high', '0'), "Số chai cao")

            # Ép về biên để tránh total sai (tuỳ bạn: nếu muốn “bắt nhập lại” thì bỏ 3 dòng clamp này)
            qty_low = max(0, min(10, qty_low))
            qty_mid = max(0, min(10, qty_mid))
            qty_high = max(0, min(10, qty_high))

            # 3) Rule: phải chọn ít nhất 1 chai
            if (qty_low + qty_mid + qty_high) == 0:
                errors.append("Vui lòng chọn ít nhất 1 chai (thấp/trung/cao) để đặt hàng.")

            # 4) Build data để đổ lại form khi lỗi
            data = {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'birth_year': birth_year,
                'address': address,
                'qty_low': qty_low,
                'qty_mid': qty_mid,
                'qty_high': qty_high,
                'delivery_date': delivery_raw,
            }

            # 5) Nếu có lỗi -> render lại, KHÔNG mở popup confirm
            if errors:
                ctx.update({
                    'form': data,
                    'data': data,
                    'errors': errors,
                    'show_confirm': False,
                    'show_paid': False,
                    'show_pay': False,
                })
                return render(request, 'orders/orders_form.html', ctx)

            # 6) Không lỗi -> tính toán & show confirm
            total = qty_low * 50 + qty_mid * 60 + qty_high * 70

            delivery_obj = parse_date(delivery_raw)
            delivery_date_display = delivery_obj.strftime("%d-%m-%Y") if delivery_obj else delivery_raw
            total_display = f"{total:,}".replace(",", ".") + " VNĐ"

            request.session['pending_order'] = {
                "form": data,
                "total": total,
                "total_display": total_display,
                "delivery_date_display": delivery_date_display,
            }

            ctx.update({
                'form': data,
                'data': data,
                'total': total,
                'total_display': total_display,
                'delivery_date_display': delivery_date_display,
                'show_confirm': True,
                'show_paid': False
            })
            return render(request, 'orders/orders_form.html', ctx)

        elif stage == "qr":
            pending = request.session.get("pending_order") or {}
            form = pending.get("form", {})
            ctx.update({
                "form": form,
                "data": form,
                "show_confirm": False,
                "show_pay": True,  # nhớ template phải dùng đúng biến này
                "show_paid": False,
                "total_display": pending.get("total_display", ""),
                "delivery_date_display": pending.get("delivery_date_display", ""),
            })
            return render(request, "orders/orders_form.html", ctx)

        elif stage == "pay":
            pending = request.session.get("pending_order") or {}
            form = pending.get("form")
            if not form:
                return redirect("orders:orders_form")
            # parse ngày
            delivery_obj, _delivery_display = _parse_delivery_date(form.get("delivery_date", ""))
            # tạo order (NHỚ dùng đúng tên field trong model của bạn)
            order = (Order.objects.create(
                full_name=form.get("full_name", ""),
                phone=form.get("phone", ""),
                email=form.get("email", ""),
                birth_year=int(form.get("birth_year") or 0),
                address=form.get("address", ""),
                qty_low=int(form.get("qty_low") or 0),
                qty_mid=int(form.get("qty_mid") or 0),
                qty_high=int(form.get("qty_high") or 0),
                delivery_date=delivery_obj,
                # nếu model bạn là total_price thì dùng total_price
                total_price=int(pending.get("total") or 0),
                is_paid=True,
                paid_at=timezone.now(),
            ))
            request.session.pop("pending_order", None)

            ctx.update({
                "form": {},  # nếu muốn xóa form sau khi thanh toán
                "data": form,  # hoặc {} tùy bạn
                "show_confirm": False,
                "show_pay": False,
                "show_paid": True,
                "order_id": order.id,
                "total_display": pending.get("total_display", _format_vnd(order.total_price)),
                "delivery_date_display": pending.get("delivery_date_display", _delivery_display),
            })
            return render(request, "orders/orders_form.html", ctx)
        return render(request, "orders/orders_form.html", ctx)
    return render(request, "orders/orders_form.html", ctx)

