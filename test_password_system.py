#!/usr/bin/env python
"""
密码管理系统测试用例
测试用户注册、登录、团队管理、密码管理等功能
"""

import requests
import time
import json
from urllib.parse import urljoin

class PasswordSystemTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        # 固定超级管理员账号
        self.admin_username = "yunda_98091723"
        self.admin_password = "%aaNdQYB3Xz:at6"
        
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = f"{status} {test_name}: {message}"
        self.test_results.append(result)
        print(result)
        
    def get_csrf_token(self, url):
        """获取CSRF令牌"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                # 简单的CSRF令牌提取（实际项目中可能需要更复杂的解析）
                if 'csrfmiddlewaretoken' in response.text:
                    import re
                    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
                    if csrf_match:
                        return csrf_match.group(1)
            return None
        except Exception as e:
            print(f"获取CSRF令牌失败: {e}")
            return None
    
    def test_1_homepage_access(self):
        """测试首页访问"""
        try:
            response = self.session.get(self.base_url)
            success = response.status_code in [200, 302]  # 200或重定向到登录页
            self.log_test("首页访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("首页访问", False, f"异常: {e}")
            return False
    
    def test_2_login_page_access(self):
        """测试登录页面访问"""
        try:
            response = self.session.get(f"{self.base_url}/accounts/login/")
            success = response.status_code == 200
            self.log_test("登录页面访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("登录页面访问", False, f"异常: {e}")
            return False
    
    def test_3_register_page_access(self):
        """测试注册页面访问"""
        try:
            response = self.session.get(f"{self.base_url}/accounts/register/")
            success = response.status_code == 200
            self.log_test("注册页面访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("注册页面访问", False, f"异常: {e}")
            return False
    
    def admin_login(self):
        """用超级管理员账号登录"""
        login_url = f"{self.base_url}/accounts/login/"
        csrf_token = self.get_csrf_token(login_url)
        if not csrf_token:
            self.log_test("超级管理员登录", False, "无法获取CSRF令牌")
            return False
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': self.admin_username,
            'password': self.admin_password
        }
        response = self.session.post(login_url, data=data)
        success = response.status_code == 302
        self.log_test("超级管理员登录", success, f"状态码: {response.status_code}")
        return success

    def test_4_user_registration(self):
        """测试用户注册（用超级管理员身份）"""
        # 先用超级管理员登录
        if not self.admin_login():
            self.log_test("用户注册", False, "超级管理员登录失败")
            return False
        try:
            register_url = f"{self.base_url}/accounts/register/"
            csrf_token = self.get_csrf_token(register_url)
            if not csrf_token:
                self.log_test("用户注册", False, "无法获取CSRF令牌")
                return False
            timestamp = int(time.time())
            username = f"testuser_{timestamp}"
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'username': username,
                'email': f"{username}@test.com",
                'password': 'TestPass123!'
            }
            response = self.session.post(register_url, data=data)
            success = response.status_code in [200, 302]
            self.log_test("用户注册", success, f"用户: {username}, 状态码: {response.status_code}")
            if success:
                self.test_username = username
                self.test_password = 'TestPass123!'
            return success
        except Exception as e:
            self.log_test("用户注册", False, f"异常: {e}")
            return False
    
    def test_5_user_login(self):
        """测试普通用户登录"""
        try:
            if not hasattr(self, 'test_username'):
                self.log_test("用户登录", False, "未找到测试用户")
                return False
            login_url = f"{self.base_url}/accounts/login/"
            csrf_token = self.get_csrf_token(login_url)
            if not csrf_token:
                self.log_test("用户登录", False, "无法获取CSRF令牌")
                return False
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'username': self.test_username,
                'password': self.test_password
            }
            response = self.session.post(login_url, data=data)
            success = response.status_code == 302
            self.log_test("用户登录", success, f"用户: {self.test_username}, 状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("用户登录", False, f"异常: {e}")
            return False
    
    def test_6_dashboard_access(self):
        """测试Dashboard访问"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard/")
            success = response.status_code == 200
            self.log_test("Dashboard访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Dashboard访问", False, f"异常: {e}")
            return False
    
    def test_7_team_creation(self):
        """测试团队创建"""
        try:
            team_create_url = f"{self.base_url}/teams/create/"
            csrf_token = self.get_csrf_token(team_create_url)
            
            if not csrf_token:
                self.log_test("团队创建", False, "无法获取CSRF令牌")
                return False
            
            timestamp = int(time.time())
            team_name = f"测试团队_{timestamp}"
            
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'name': team_name,
                'description': '这是一个测试团队'
            }
            
            response = self.session.post(team_create_url, data=data)
            success = response.status_code == 302  # 创建成功会重定向
            self.log_test("团队创建", success, f"团队: {team_name}, 状态码: {response.status_code}")
            
            if success:
                self.test_team_name = team_name
            
            return success
        except Exception as e:
            self.log_test("团队创建", False, f"异常: {e}")
            return False
    
    def test_8_password_creation(self):
        """测试密码创建"""
        try:
            password_add_url = f"{self.base_url}/passwords/add/"
            csrf_token = self.get_csrf_token(password_add_url)
            
            if not csrf_token:
                self.log_test("密码创建", False, "无法获取CSRF令牌")
                return False
            
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'title': '测试密码',
                'website': 'https://example.com',
                'username': 'testuser',
                'password': 'TestPassword123!',
                'notes': '这是一个测试密码条目'
            }
            
            response = self.session.post(password_add_url, data=data)
            success = response.status_code == 302  # 创建成功会重定向
            self.log_test("密码创建", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("密码创建", False, f"异常: {e}")
            return False
    
    def test_9_password_viewing(self):
        """测试密码查看"""
        try:
            # 先访问dashboard获取密码列表
            dashboard_response = self.session.get(f"{self.base_url}/dashboard/")
            if dashboard_response.status_code != 200:
                self.log_test("密码查看", False, "无法访问dashboard")
                return False
            
            # 尝试访问第一个密码（如果存在）
            response = self.session.get(f"{self.base_url}/passwords/1/")
            success = response.status_code in [200, 404]  # 200表示有密码，404表示没有密码
            self.log_test("密码查看", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("密码查看", False, f"异常: {e}")
            return False
    
    def test_10_password_generation(self):
        """测试密码生成API"""
        try:
            response = self.session.get(f"{self.base_url}/passwords/generate/?length=16&symbols=true")
            success = response.status_code == 200
            
            if success:
                try:
                    data = response.json()
                    has_password = 'password' in data
                    self.log_test("密码生成API", has_password, f"生成密码: {data.get('password', 'N/A')[:10]}...")
                    return has_password
                except json.JSONDecodeError:
                    self.log_test("密码生成API", False, "返回的不是有效JSON")
                    return False
            else:
                self.log_test("密码生成API", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("密码生成API", False, f"异常: {e}")
            return False
    
    def test_11_team_list_access(self):
        """测试团队列表访问"""
        try:
            response = self.session.get(f"{self.base_url}/teams/")
            success = response.status_code == 200
            self.log_test("团队列表访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("团队列表访问", False, f"异常: {e}")
            return False
    
    def test_12_user_list_access(self):
        """测试用户列表访问"""
        try:
            response = self.session.get(f"{self.base_url}/accounts/users/")
            success = response.status_code == 200
            self.log_test("用户列表访问", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("用户列表访问", False, f"异常: {e}")
            return False
    
    def test_13_logout(self):
        """测试用户登出"""
        try:
            response = self.session.get(f"{self.base_url}/accounts/logout/")
            success = response.status_code == 302  # 登出会重定向到登录页
            self.log_test("用户登出", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("用户登出", False, f"异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行密码管理系统测试...")
        print("=" * 60)
        
        # 基础功能测试
        self.test_1_homepage_access()
        self.test_2_login_page_access()
        self.test_3_register_page_access()
        
        # 用户管理测试
        if self.test_4_user_registration():
            if self.test_5_user_login():
                # 登录成功后的功能测试
                self.test_6_dashboard_access()
                self.test_7_team_creation()
                self.test_8_password_creation()
                self.test_9_password_viewing()
                self.test_10_password_generation()
                self.test_11_team_list_access()
                self.test_12_user_list_access()
                self.test_13_logout()
        
        # 输出测试总结
        print("=" * 60)
        print("📊 测试总结:")
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests == 0:
            print("🎉 所有测试都通过了！")
        else:
            print("⚠️  有测试失败，请检查相关功能。")

def main():
    """主函数"""
    print("密码管理系统测试工具")
    print("请确保Django服务器正在运行 (python manage.py runserver)")
    
    # 创建测试器实例
    tester = PasswordSystemTester()
    
    # 运行所有测试
    tester.run_all_tests()

if __name__ == "__main__":
    main() 