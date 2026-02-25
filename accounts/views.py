from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def register(request):
    # GET: nếu có reg_ok trong session thì mở modal
    reg_ok = request.session.pop('reg_ok', None)

    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()
        pw1 = request.POST.get('password1','')
        pw2 = request.POST.get('password2','')

        if not username or not pw1 or not pw2:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return redirect('register')

        if pw1 != pw2:
            messages.error(request, "Mật khẩu xác nhận không khớp.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại.")
            return redirect('register')

        # tạo user
        user = User.objects.create_user(username=username, password=pw1)
        if email:
            user.email = email
            user.save()

        # lưu info để popup hiển thị (đồ án demo; thực tế không nên show mật khẩu)
        request.session['reg_ok'] = {
            'username': username,
            'email': email,
            'password': pw1,  # demo theo yêu cầu
        }
        return redirect('register')  # PRG pattern (refresh không tạo lại)
    return render(request, 'accounts/register.html', {'reg_ok': reg_ok})

def register_success(request):
    username = request.session.get('reg_username')
    if not username:
        return redirect('register')
    return render(request, 'accounts/register_success.html', {'username': username})

def password_reset_demo(request):
    """
    Demo đúng mô tả: nhập email -> nếu đúng thì cho đặt lại mật khẩu.
    (Đồ án demo OK, thực tế nên gửi email reset link.)
    """
    context = {'step': 1, 'email_ok': False}

    if request.method == 'POST':
        step = int(request.POST.get('step', '1'))
        email = request.POST.get('email', '').strip()
        context['email'] = email

        if step == 1:
            # demo: tìm user theo email
            user = User.objects.filter(email=email).first()
            if user:
                context['step'] = 2
                context['email_ok'] = True
                request.session['reset_user_id'] = user.id
            else:
                context['step'] = 1
                messages.error(request, "Email sai, vui lòng nhập lại.")
        else:
            pw1 = request.POST.get('password1','')
            pw2 = request.POST.get('password2','')
            uid = request.session.get('reset_user_id')

            if not uid:
                messages.error(request, "Phiên đặt lại mật khẩu đã hết hạn.")
                return redirect('password_reset_demo')

            if pw1 != pw2 or not pw1:
                messages.error(request, "Mật khẩu không hợp lệ hoặc không khớp.")
                context['step'] = 2
                context['email_ok'] = True
            else:
                user = User.objects.filter(id=uid).first()
                if user:
                    user.set_password(pw1)
                    user.save()
                    messages.success(request, "Đặt lại mật khẩu thành công. Hãy đăng nhập.")
                    request.session.pop('reset_user_id', None)
                    return redirect('login')

    return render(request, 'accounts/password_reset_demo.html', context)
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.conf import settings

def login_view(request):
    ctx = {
        'open_forgot': (request.GET.get('forgot') == '1'),
        'forgot_step': 1,
    }

    # login success modal (PRG)
    if request.session.pop('login_ok', None):
        ctx['login_success'] = True

    # reset success modal
    if request.session.pop('reset_ok', None):
        ctx['reset_success'] = True

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'login')

        # 1) LOGIN FORM
        if form_type == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                # Nếu là admin
                if user.is_staff or user.is_superuser:
                    return redirect('admin_dashboard')
                # Nếu là user thường
                return redirect('home')
            else:
                ctx['login_error'] = True

        # 2) FORGOT STEP 1: CHECK EMAIL
        elif form_type == 'forgot_email':
            email = request.POST.get('email', '').strip()
            ctx['open_forgot'] = True
            ctx['email'] = email
            user = User.objects.filter(email=email).first()
            if user:
                request.session['reset_uid'] = user.id
                ctx['forgot_step'] = 2
            else:
                ctx['forgot_step'] = 1
                ctx['forgot_error'] = "Email sai, vui lòng nhập lại."

        # 3) FORGOT STEP 2: RESET PASSWORD
        elif form_type == 'forgot_reset':
            pw1 = request.POST.get('password1','')
            pw2 = request.POST.get('password2','')
            ctx['open_forgot'] = True
            ctx['forgot_step'] = 2

            uid = request.session.get('reset_uid')
            if not uid:
                ctx['forgot_error'] = "Phiên đặt lại mật khẩu đã hết hạn. Hãy thử lại."
                ctx['forgot_step'] = 1
            elif not pw1 or pw1 != pw2:
                ctx['forgot_error'] = "Mật khẩu không hợp lệ hoặc không khớp."
            else:
                user = User.objects.filter(id=uid).first()
                if not user:
                    ctx['forgot_error'] = "Không tìm thấy tài khoản. Hãy thử lại."
                    ctx['forgot_step'] = 1
                else:
                    user.set_password(pw1)
                    user.save()
                    request.session.pop('reset_uid', None)
                    request.session['reset_ok'] = True
                    return redirect('/login/')  # mở modal reset thành công

    return render(request, 'accounts/login.html', ctx)

from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

@require_POST
def logout_view(request):
    logout(request)
    request.session.pop('is_site_admin', None)  # xoá trang thái đăng nhập admin nếu có
    return redirect("/")
