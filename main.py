import tweepy
import re
import config
import time
import requests
import random
from datetime import timezone, timedelta
from requests_oauthlib import OAuth1
import logging
import os.path
import html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logfile = os.path.join(BASE_DIR, 'test.log')

logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

class TwitterBot:

  # initialization
  def __init__(self, checked = 0, posted = 0, notsent = 0, dms = 0):
    self.auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    self.auth.set_access_token(config.access_token, config.access_token_secret)
    self.api = tweepy.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    self.me = self.api.me()
    self.posted = posted #number of dm posted
    self.checked = checked #number of dm checked
    self.notsent = notsent #number of incoming dm not sent
    self.dms = dms

  def checkdm(self):
    api = self.api
    dms = api.list_direct_messages()
    for i, dm in enumerate(reversed(dms)):
      logging.info(f"DM No. {i+1}: {dm.message_create['message_data']['text'].encode('utf-8')}")
    self.dms = dms
    self.checked = len(dms)
    return self.dms

  def post_all(self, dms, checked=0, posted=0, notsent=0):
    """Post all incoming DMs that contain the trigger word. 
    
    Arg:
      dms (list of direct messages objects), from checkdm() function

    """
        
    api = self.api
    
    logging.info(f'Total DM = {len(dms)}')

    for i, dm in enumerate(reversed(dms)):
      dmsender = int(dm.message_create['sender_id'])
      urls = dm.message_create['message_data']['entities']['urls']
      tweet = html.unescape(dm.message_create['message_data']['text'])
      if dmsender == self.me.id:
        continue
      elif config.trigger in tweet:
        linkcontent = None
        media_ids = None
        if 'attachment' in dm.message_create['message_data']:
          if dm.message_create['message_data']['attachment']['media']['type'] == 'photo':
            media_url = dm.message_create['message_data']['attachment']['media']['media_url']
            media_id = self.tweet_attachment(media_url)
            media_ids = []
            media_ids.append(media_id)
            tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|(\w+:\/\/\S+)", " ",tweet).split())
          else:
            self.senddm(i, dmsender, status='wrong attachment')
            continue
        
        elif len(urls) >0:
          linkcontent = urls[0]['expanded_url']
          if 'photo' in linkcontent or 'video' in linkcontent:
            linkcontent = None
          elif 'twitter.com' in linkcontent:
            tweet = ' '.join(re.sub("(\w+:\/\/\S+)", " ",tweet).split())
          else: linkcontent = None
            
        complete = 0
        while len(tweet) > 280:
          leftcheck = 260
          left = 0
          right = 272
          check = tweet[leftcheck:right].split(' ')
          separator = len(check[-1])
          tweet1 = tweet[left:right-separator] + '(cont..)'
              
          if complete == 0:
            try:
              sendtwt = api.update_status(tweet1, media_ids=media_ids, attachment_url=linkcontent)
              time.sleep(10)
            except tweepy.error.TweepError as e:
              logging.error(e)
              continue

            posted += 1
            complete = sendtwt.id
            postid = complete
            rttime = sendtwt.created_at.replace(tzinfo=timezone.utc)		
          else: complete = api.update_status(tweet1, in_reply_to_status_id = complete, auto_populate_reply_metadata = True).id
          time.sleep(10)
          tweet = tweet[right-separator:len(tweet)]

        if complete == 0:
          try:
            sendtwt = api.update_status(tweet, media_ids=media_ids, attachment_url=linkcontent)
          except tweepy.error.TweepError as e:
            logging.error(e)
            continue
          
          rttime = sendtwt.created_at.replace(tzinfo=timezone.utc)
          postid = sendtwt.id
          posted +=1
          
        else:
          api.update_status(tweet, in_reply_to_status_id = complete, auto_populate_reply_metadata = True)
                  
        self.senddm(i, dmsender, status='sent', postid=postid, rttime=rttime)
        api.destroy_direct_message(int(dm.id))
        logging.info('Finished.')
        time.sleep(60+random.randrange(0,60,15))
      
      else:
        self.senddm(i, dmsender, status='notsent')
        api.destroy_direct_message(int(dm.id))
        notsent +=1
    self.posted = posted
    self.checked = len(dms)
    self.notsent = notsent
    self.dms = dms
    
    logging.info('DM has been checked')
    
    time.sleep(3)

    return

  # Notifies the DM sender. Modify your message here.
  def senddm(self, i, dmsender, status, postid=None, rttime=None):
    api = self.api
    url = 'https://twitter.com/'+self.me.screen_name+'/status/'+str(postid)
    if status == 'sent':
      message = {'sent': 'Post was successfully sent at '+rttime.astimezone(timezone(timedelta(hours=config.timezone))).strftime("%Y-%m-%d %H:%M")+' WIB. Check your post here: '+url}
    elif status == 'notsent':
      message = {'notsent' : 'Post was not sent. Use the trigger '+config.trigger+' to send post.'}
    else: message = {'wrong attachment' : 'Post was not sent. Send only picture attachment (not gif/video).'}

    notifdm = api.send_direct_message(recipient_id=dmsender, text=message[status])
    #api.destroy_direct_message(int(notifdm.id))
    logging.info(f'DM No {i+1} was sent. Status = {status}')
    time.sleep(10)
    
    return

  
  def tweet_attachment(self, media_url):
    api = self.api
    oauth = OAuth1(client_key = config.consumer_key, client_secret = config.consumer_secret, resource_owner_key = config.access_token, resource_owner_secret = config.access_token_secret)
    r = requests.get(media_url, auth = oauth)
    filename = 'temp.jpg'
    if r.status_code == 200:
      with open(filename, 'wb') as image:
        for chunk in r:
          image.write(chunk)
      media_ids = api.media_upload(filename).media_id
    return media_ids

  
  def delete_dm(self, dms):
    api = self.api
    for dm in dms:
      if dm.id == self.me.id:
        try: api.destroy_direct_message(dm.id)
        except tweepy.error.TweepError as e:
          logging.error(e)
          continue
    return
  
  def delete_all(self, dms):
    api = self.api
    for dm in dms:
      try: api.destroy_direct_message(dm.id)
      except tweepy.error.TweepError as e:
          logging.error(e)
          continue
    return  
    
  def __str__(self):
    logging.info(f"DM counts: {self.checked}, DM posted: {self.posted}, DM not sent: {self.notsent}")
    dmcontent = """
    DM counts : {}
    DM posted : {}
    DM not sent : {}
    """.format(self.checked, self.posted, self.notsent)
    return dmcontent
  
  def __repr__(self):
    return f"DM counts: {self.checked}, DM posted: {self.posted}, DM not sent: {self.notsent}"
