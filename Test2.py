a = "15元"
print(a[-1])
print(a[:-1])

b = "已售322"
print(b.find("售"))
print(b[b.find("售")+1:])


aaa = {"name":"123"}
if aaa["name"]:
    print(123)

bbb = "100元"
print(bbb[:-1])

ccc = "¥25.6 限时抢购"
if "¥" in ccc or "限时抢购" in ccc:
    index = ccc.find("限时抢购")
    print(index)
    temp = ccc[1:index].strip()
    try:
        temp = float(temp)
    except:
        temp = 0.0
    print(temp)

print()

# if条件判断认为：1、字符串非空、数字非0、数字非0.0 为True；2、字符串空、数字0、数字0.0 为False：
package = {}
package['market_price'] = 0.0
package['market_price2'] = ""
package['market_price3'] = "666"
package['market_price4'] = 0
package['market_price5'] = 1
package['market_price6'] = 1.1
if package['market_price']:
    print(111)
if package['market_price2']:
    print(222)
if package['market_price3']:
    print(333) # 打印
if package['market_price4']:
    print(444)
if package['market_price5']:
    print(555) # 打印
if package['market_price6']:
    print(666) # 打印
print()
if not package['market_price']:
    print(111) # 打印
if not package['market_price2']:
    print(222) # 打印
if not package['market_price3']:
    print(333)
if not package['market_price4']:
    print(444) # 打印
if not package['market_price5']:
    print(555)
if not package['market_price6']:
    print(666)