# def import_china_provinces_yesterday():
# 	print("Uploading China provinces")
# 	from datetime import datetime, timedelta
# 	yesterday = (datetime.utcnow().date() + timedelta(days=-1))
# 	url = yesterday.strftime("http://49.4.25.117/JKZX/yq_%Y%m%d.json")
# 	return import_json(
# 		url=url,
# 		source_link="https://ncov.dxy.cn/ncovh5/view/en_pneumonia",
# 		table_labels={
# 			"datapoint": {
# 				"country": "China",
# 				"province": ["properties", "省份", "::china_province_eng"],
# 				"total": ["properties", "累计确诊"],
# 				"deaths": ["properties", "累计死亡"],
# 				"entry_date": yesterday
# 			}
# 		},
# 		namespace=["features"]
# 	)