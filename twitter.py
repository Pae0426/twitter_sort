import os
import tweepy
import requests
import datetime

TWITTER_API_KEY=os.environ['TWITTER_API_KEY']
TWITTER_API_SECRET_KEY=os.environ['TWITTER_API_SECRET_KEY']
TWITTER_ACCESS_TOKEN=os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_TOKEN_SECRET=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
SLACK_INCOMING_WEBHOOK_URL = os.environ['SLACK_INCOMING_WEBHOOK_URL']

# 認証情報を設定する。
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)  # APIクライアントを取得する。

def main():
    searchTweets('あつ森 min_faves:1000',10)

def searchTweets(keyword,num):
    print(keyword)
    tweets_dict={}
    tweets = tweepy.Cursor(api.search,q=keyword,tweet_mode='extended',lang='ja').items(100)
    count=0
    for tweet in tweets:
        count+=1
        fav=tweet.favorite_count
        tweet_info=[str(tweet.id),tweet.user.name,tweet.full_text]
        if len(tweets_dict)<num:
            tweets_dict[fav]=tweet_info
        else:
            min_fav=min(tweets_dict)
            if min_fav<fav:
                del tweets_dict[min_fav]
                tweets_dict[fav]=tweet_info
    
    print('count:'+str(count))
    top10_fav=sorted(tweets_dict,reverse=True)
    print(top10_fav)

    date=datetime.datetime.now()
    requests.post(SLACK_INCOMING_WEBHOOK_URL,json={
        'text':f'取得日時：{date.year}/{date.month}/{date.day} {date.hour}:{date.minute}'
    })
    for top_tweet in top10_fav:
        requests.post(SLACK_INCOMING_WEBHOOK_URL, json={
            'text': f'【いいね】{top_tweet}\n【ユーザー名】{tweets_dict[top_tweet][1]}\n【ツイート】\n{tweets_dict[top_tweet][2]}\n----------------------------------------',
            'unfurl_links': True,  # リンクのタイトルや画像を表示する。
        })
    
    
    with open('top10_tweet.txt','w') as file:
        rank=1
        for top_tweet in top10_fav:
            #file.write('ユーザーID:' + dict_[top_tweet][0]+'\n')
            file.write(str(rank)+'位\n')
            file.write('ユーザー名:' + tweets_dict[top_tweet][1]+'\n')
            file.write('いいね数  :' + str(top_tweet)+'\n')
            file.write('ツイート  :' + tweets_dict[top_tweet][2]+'\n')
            file.write('***********************************************************************************'+'\n')
            rank+=1
    
    
    print("API.search")
    print(api.rate_limit_status()["resources"]["search"]["/search/tweets"],"\n" +"-"*50)

if __name__=='__main__':
    main()