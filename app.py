from main import TwitterBot

if __name__ == '__main__':
  session = TwitterBot()
  a = session.checkdm()
  session.post_all(a)
  session