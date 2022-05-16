import pymysql

# 此方法用来替代全局的 SQLclient
pymysql.install_as_MySQLdb()
# Django会帮你建表不会帮你建库
# python manage.py migrate初始化数据库完成第一次迁移生成第一次管理表