# UITest
![image](https://github.com/jaylion321/UITest/blob/master/docIMG/UI.PNG)
Readme EX : https://github.com/openatx/uiautomator2/blob/master/README.md

#UI Design
![image](https://github.com/jaylion321/UITest/blob/master/docIMG/UIDesign1.PNG)
![image](https://github.com/jaylion321/UITest/blob/master/docIMG/UIDesign2.PNG)


**[Development Diary](#development-diary)**
  - **[2020/11/08](#20201108)**
  - **[2020/11/09](#20201109)**
  - **[2020/11/16](#20201116)**
  
### Development Diary
#### 2020/11/08
```python
      '''judge if input is an valid ip'''
      for i,proxyip in enumerate(Text):
          regx_ip = re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$',proxyip)
          if( re.split  != None and [0<=int(x)<256 for x in re.split('[\.]',re.split(':', regx_ip.group(0))[0]) ].count(True)==4 ):
              proxy_list.append(proxyip)
```
#### 2020/11/09
#### 2020/11/16