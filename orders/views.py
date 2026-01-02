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
            data = \
            {
                'full_name': request.POST.get('full_name','').strip(),
                'phone': request.POST.get('phone','').strip(),
                'email': request.POST.get('email','').strip(),
                'birth_year': request.POST.get('birth_year','').strip(),
                'address': request.POST.get('address','').strip(),
                'qty_low': int(request.POST.get('qty_low','0') or 0),
                'qty_mid': int(request.POST.get('qty_mid','0') or 0),
                'qty_high': int(request.POST.get('qty_high','0') or 0),
                'delivery_date': request.POST.get('delivery_date','').strip(),
            }
            total = data['qty_low'] * 50 + data['qty_mid'] * 60 + data['qty_high'] * 70

            delivery_raw = data.get("delivery_date", "")
            delivery_obj = parse_date(delivery_raw)  # yyyy-mm-dd -> date hoặc None

            delivery_date_display = delivery_obj.strftime("%d-%m-%Y") if delivery_obj else delivery_raw
            total_display = f"{total:,}".replace(",", ".") + " VNĐ"

            request.session['pending_order'] = \
            {
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

