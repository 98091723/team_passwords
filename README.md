# 团队密码管理系统

一个基于Django的现代化团队密码管理系统，支持个人和团队密码管理，具备完善的权限控制和加密存储功能。

## 🚀 主要功能

### 🔐 密码管理
- **个人密码管理** - 用户可以管理自己的个人密码
- **团队密码共享** - 团队成员可以共享和管理团队密码
- **密码加密存储** - 使用AES加密算法保护密码安全
- **强密码生成** - 内置强密码生成器
- **密码分类管理** - 支持按团队和个人分类管理

### 👥 团队管理
- **团队创建** - 用户可以创建和管理团队
- **成员管理** - 支持添加、移除团队成员
- **权限控制** - 团队管理员和普通成员权限分离
- **团队密码共享** - 团队成员可以共享密码

### 🔒 权限控制
- **超级管理员** - 可以管理所有用户和密码
- **团队管理员** - 可以管理团队内的密码和成员
- **普通用户** - 只能管理自己的个人密码和所在团队的密码
- **细粒度权限** - 基于角色的访问控制

### 🛡️ 安全特性
- **密码加密存储** - 使用AES-256加密算法
- **用户认证** - 安全的用户登录和会话管理
- **CSRF保护** - 防止跨站请求伪造攻击
- **权限验证** - 严格的权限检查和验证

## 🛠️ 技术栈

- **后端框架**: Django 4.2.7
- **数据库**: SQLite (可扩展至PostgreSQL/MySQL)
- **前端**: Bootstrap 5 + jQuery
- **加密**: AES-256加密算法
- **认证**: Django内置认证系统

## 📦 安装和运行

### 1. 克隆项目
```bash
git clone https://github.com/98091723/team_passwords.git
cd team_passwords
```

### 2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级管理员
```bash
python manage.py createsuperuser
```

### 6. 运行开发服务器
```bash
python manage.py runserver
```

访问 http://localhost:8000 开始使用

## 📁 项目结构

```
team_passwords/
├── accounts/          # 用户管理应用
│   ├── views.py      # 用户认证和注册视图
│   ├── urls.py       # 用户相关URL配置
│   └── templates/    # 用户相关模板
├── passwords/         # 密码管理应用
│   ├── views.py      # 密码CRUD视图
│   ├── models.py     # 密码数据模型
│   ├── urls.py       # 密码相关URL配置
│   └── templates/    # 密码相关模板
├── teams/            # 团队管理应用
│   ├── views.py      # 团队管理视图
│   ├── models.py     # 团队数据模型
│   ├── urls.py       # 团队相关URL配置
│   └── templates/    # 团队相关模板
├── utils/            # 工具模块
│   └── crypto.py     # 加密工具类
├── templates/        # 全局模板
├── static/           # 静态文件
└── team_passwords/   # 项目配置
    ├── settings.py   # Django设置
    ├── urls.py       # 主URL配置
    └── wsgi.py       # WSGI配置
```

## 🔧 配置说明

### 环境变量
在 `team_passwords/settings.py` 中可以配置以下设置：

- `SECRET_KEY` - Django密钥
- `DEBUG` - 调试模式
- `ALLOWED_HOSTS` - 允许的主机
- `DATABASES` - 数据库配置

### 加密配置
加密相关的配置在 `utils/crypto.py` 中：

- 加密算法：AES-256
- 密钥派生：基于用户名和盐值
- 盐值长度：32字节

## 📖 使用指南

### 1. 首次使用
1. 访问系统首页
2. 使用超级管理员账号登录
3. 创建团队和用户
4. 开始管理密码

### 2. 创建团队
1. 登录后点击"团队管理"
2. 点击"创建团队"
3. 填写团队名称和描述
4. 添加团队成员

### 3. 添加密码
1. 在Dashboard点击"添加密码"
2. 填写密码信息（标题、网站、用户名、密码）
3. 选择是否为团队密码
4. 保存密码条目

### 4. 管理密码
- **查看密码**: 点击密码条目查看详情
- **编辑密码**: 点击编辑按钮修改密码信息
- **删除密码**: 点击删除按钮移除密码条目
- **复制密码**: 在密码详情页面可以复制密码

## 🔒 安全建议

1. **定期更换密码** - 建议定期更换系统密码
2. **使用强密码** - 使用系统生成的强密码
3. **权限管理** - 合理分配用户权限
4. **日志监控** - 定期检查系统日志
5. **备份数据** - 定期备份重要数据

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目链接: [https://github.com/98091723/team_passwords](https://github.com/98091723/team_passwords)
- 问题反馈: [Issues](https://github.com/98091723/team_passwords/issues)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！ 