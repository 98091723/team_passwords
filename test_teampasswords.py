import requests
from bs4 import BeautifulSoup
import random, string, time

BASE_URL = "https://teampasswords-production.up.railway.app"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
DASHBOARD_URL = f"{BASE_URL}/dashboard/"
TEAM_URL = f"{BASE_URL}/teams/"
TEAM_ADD_URL = f"{BASE_URL}/teams/add/"
USER_LIST_URL = f"{BASE_URL}/accounts/users/"
USER_REGISTER_URL = f"{BASE_URL}/accounts/register/"
PASSWORD_ADD_URL = f"{BASE_URL}/passwords/add/"
USERNAME = "yunda_98091723"
PASSWORD = "!8a%y^*>#-DXLV#"

session = requests.Session()

def get_csrf_token(url):
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
    return token_tag.get("value") if token_tag else None

def random_str(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# 1. 登录超级管理员
def admin_login():
    csrf_token = get_csrf_token(LOGIN_URL)
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "csrfmiddlewaretoken": csrf_token,
    }
    headers = {"Referer": LOGIN_URL}
    login_resp = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    if "dashboard" in login_resp.url or "密码管理" in login_resp.text:
        print("✅ 超级管理员登录成功")
        return True
    print("❌ 超级管理员登录失败")
    return False

# 2. 创建团队
def create_team():
    team_name = "AutoTeam_" + random_str()
    csrf_token = get_csrf_token(TEAM_ADD_URL)
    team_data = {
        "name": team_name,
        "description": "自动化脚本创建",
        "csrfmiddlewaretoken": csrf_token,
    }
    resp = session.post(TEAM_ADD_URL, data=team_data, headers={"Referer": TEAM_ADD_URL})
    if team_name in resp.text:
        print(f"✅ 团队创建成功: {team_name}")
        return team_name
    print("❌ 团队创建失败")
    return None

# 3. 添加个人密码
def add_personal_password():
    csrf_token = get_csrf_token(PASSWORD_ADD_URL)
    pwd_title = "AutoPwd_" + random_str()
    pwd_data = {
        "title": pwd_title,
        "website": "https://example.com",
        "username": "testuser",
        "password": "Test@123456",
        "notes": "个人密码自动化添加",
        "csrfmiddlewaretoken": csrf_token,
    }
    resp = session.post(PASSWORD_ADD_URL, data=pwd_data, headers={"Referer": PASSWORD_ADD_URL})
    if pwd_title in resp.text or "密码添加成功" in resp.text:
        print(f"✅ 个人密码添加成功: {pwd_title}")
        return pwd_title
    print("❌ 个人密码添加失败")
    return None

# 4. 添加团队密码
def add_team_password(team_name):
    # 获取团队id
    team_list_resp = session.get(TEAM_URL)
    soup = BeautifulSoup(team_list_resp.text, "html.parser")
    team_id = None
    for a in soup.find_all("a", href=True):
        if team_name in a.text:
            # /teams/1/ 取数字
            parts = a['href'].strip('/').split('/')
            if len(parts) >= 2 and parts[0] == 'teams':
                team_id = parts[1]
                break
    if not team_id:
        print("❌ 未找到团队ID，无法添加团队密码")
        return None
    csrf_token = get_csrf_token(PASSWORD_ADD_URL)
    pwd_title = "TeamPwd_" + random_str()
    pwd_data = {
        "title": pwd_title,
        "website": "https://team.com",
        "username": "teamuser",
        "password": "Team@123456",
        "notes": "团队密码自动化添加",
        "team": team_id,
        "csrfmiddlewaretoken": csrf_token,
    }
    resp = session.post(PASSWORD_ADD_URL, data=pwd_data, headers={"Referer": PASSWORD_ADD_URL})
    if pwd_title in resp.text or "密码添加成功" in resp.text:
        print(f"✅ 团队密码添加成功: {pwd_title}")
        return pwd_title, team_id
    print("❌ 团队密码添加失败")
    return None, team_id

# 5. 编辑密码（以个人密码为例）
def edit_password(pwd_title):
    # 获取密码id
    dashboard_resp = session.get(DASHBOARD_URL)
    soup = BeautifulSoup(dashboard_resp.text, "html.parser")
    pwd_id = None
    for a in soup.find_all("a", href=True):
        if pwd_title in a.text and '/edit/' in a['href']:
            # /passwords/1/edit/ 取数字
            parts = a['href'].strip('/').split('/')
            if len(parts) >= 3 and parts[0] == 'passwords':
                pwd_id = parts[1]
                break
    if not pwd_id:
        print("❌ 未找到密码ID，无法编辑")
        return False
    edit_url = f"{BASE_URL}/passwords/{pwd_id}/edit/"
    csrf_token = get_csrf_token(edit_url)
    new_title = pwd_title + "_Edit"
    edit_data = {
        "title": new_title,
        "website": "https://edit.com",
        "username": "edituser",
        "password": "Edit@123456",
        "notes": "编辑后",
        "csrfmiddlewaretoken": csrf_token,
    }
    resp = session.post(edit_url, data=edit_data, headers={"Referer": edit_url})
    if new_title in resp.text or "保存成功" in resp.text:
        print(f"✅ 密码编辑成功: {new_title}")
        return new_title
    print("❌ 密码编辑失败")
    return False

# 6. 删除密码（以个人密码为例）
def delete_password(pwd_title):
    # 获取密码id
    dashboard_resp = session.get(DASHBOARD_URL)
    soup = BeautifulSoup(dashboard_resp.text, "html.parser")
    pwd_id = None
    for a in soup.find_all("a", href=True):
        if pwd_title in a.text and '/delete/' in a['href']:
            parts = a['href'].strip('/').split('/')
            if len(parts) >= 3 and parts[0] == 'passwords':
                pwd_id = parts[1]
                break
    if not pwd_id:
        print("❌ 未找到密码ID，无法删除")
        return False
    delete_url = f"{BASE_URL}/passwords/{pwd_id}/delete/"
    csrf_token = get_csrf_token(delete_url)
    del_data = {"csrfmiddlewaretoken": csrf_token}
    resp = session.post(delete_url, data=del_data, headers={"Referer": delete_url})
    if "删除成功" in resp.text or "密码已删除" in resp.text or "密码管理" in resp.text:
        print(f"✅ 密码删除成功: {pwd_title}")
        return True
    print("❌ 密码删除失败")
    return False

# 7. 注册普通用户并测试权限隔离
def register_and_test_user():
    # 注册
    new_username = "user_" + random_str()
    new_password = "User@123456"
    csrf_token = get_csrf_token(USER_REGISTER_URL)
    reg_data = {
        "username": new_username,
        "password": new_password,
        "email": f"{new_username}@test.com",
        "csrfmiddlewaretoken": csrf_token,
    }
    resp = session.post(USER_REGISTER_URL, data=reg_data, headers={"Referer": USER_REGISTER_URL})
    if new_username in resp.text or "创建成功" in resp.text:
        print(f"✅ 普通用户注册成功: {new_username}")
    else:
        print("❌ 普通用户注册失败")
        return
    # 新用户登录新会话
    user_sess = requests.Session()
    csrf_token = get_csrf_token(LOGIN_URL)
    login_data = {
        "username": new_username,
        "password": new_password,
        "csrfmiddlewaretoken": csrf_token,
    }
    login_resp = user_sess.post(LOGIN_URL, data=login_data, headers={"Referer": LOGIN_URL}, allow_redirects=True)
    if "dashboard" in login_resp.url or "密码管理" in login_resp.text:
        print("✅ 普通用户登录成功")
    else:
        print("❌ 普通用户登录失败")
        return
    # 权限隔离测试：访问用户列表（应被拒绝）
    user_list_resp = user_sess.get(USER_LIST_URL)
    if "权限不足" in user_list_resp.text or "dashboard" in user_list_resp.url:
        print("✅ 权限隔离：普通用户无法访问用户列表")
    else:
        print("❌ 权限隔离失败：普通用户可访问用户列表")

if __name__ == "__main__":
    if not admin_login():
        exit(1)
    team_name = create_team()
    if team_name:
        pwd_title = add_personal_password()
        if pwd_title:
            new_title = edit_password(pwd_title)
            if new_title:
                delete_password(new_title)
        add_team_password(team_name)
    register_and_test_user() 