# 配置信息

# 所爬取城市的url，以下为青岛的二手房地址
entrance_url = 	'http://qd.lianjia.com/ershoufang'
head_url = 'http://qd.lianjia.com'

# phantomJS的配置信息
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

# MongoDB的配置信息
MONGO_URL = 'localhost'
MONGO_DB = 'lianjia'
MONGO_TABLE = 'qingdao'