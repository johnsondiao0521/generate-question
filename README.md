# Generate-question based on rules  
## Steps  
0.install pyltp. [If there is problem, go here](https://blog.csdn.net/lingan_Hong/article/details/88027975)      
1.[download model](http://ltp.ai/download.html) ltpdatav3.4.0.zip to ltp_data/  
2.give sentences in client.py  
3.python3 client.py  
  
python version 3.6.5  

## Architecture
change model in ModelLoader  
add event rules in EventGenerator  
add problem rules in QuestionGenerator  
testing at any part is possible