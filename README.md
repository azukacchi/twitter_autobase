# README.md

## Description
(Very) simple twitter autobase bot that posts incoming DM

## Features
1. Posts incoming DM that contains the trigger word.
2. Posts incoming DM with media. Three ways of sending a post containing media through DM:
    - Upload your own image with the text you want to add. However, DM will not be sent if it contains uploaded attachment other than photos (example: GIF/video). The result is something like this.
    ![upload image](https://dev-to-uploads.s3.amazonaws.com/i/ir46br3cx7k86hvtuu3q.jpg)
    - Embed images/gif/video from an existing tweet by copy-pasting the link contained in a tweet with images/gif/video. Example: to embed the image from this [tweet](https://twitter.com/timeto_haechan/status/1300093500810170370), copy the text and take only the link.
    The text would be something like this:
      ```
      190831 인천 스카이 페스티벌 #NCTDREAM #NCT #해찬 #HAECHAN https://pic.twitter.com/r97xH3s15X
      ```
      Take only the link and paste it into the DM along with the text you want to add and the trigger word like below. 
      ```
      your text hereeeeee lorem ipsum triggerword https://pic.twitter.com/r97xH3s15
      ```
      The result is something like this.
      ![embed image](https://dev-to-uploads.s3.amazonaws.com/i/34zymz28b8uey2mpehl7.jpg)
   - To submit a quote-RT of a tweet, simply insert the link of the tweet.
      ```
      this is going to be sent as a quote-RT your text hereeeee triggerword https://twitter.com/timeto_haechan/status/1300093500810170370
      
      ```
      The result is something like this.
      ![quote rt](https://dev-to-uploads.s3.amazonaws.com/i/1nkyckowe9t1ysyhy5ho.jpg)

3. Cuts post longer than 280 characters and posts them as a thread. The result is something like [this](https://drive.google.com/file/d/1tNN0bW0QglARMCdUH1TAskUTtAztZjZ1/view?usp=sharing).


4. Sends a DM back for each incoming DM.
    - status `sent`: DM was successfully posted, the link to the posted tweet will be attached.
    - status `notsent`: DM was not posted because it does not contain the trigger word.
    - status `wrong attachment`: DM was not posted because it contains uploaded attachment other than photo.
5. Deletes the incoming DMs once they are posted. You can still see the content of the original DM from the link in the notification message you send back to the sender. Optional: you can also delete the notification DM you've just sent by uncommenting this line in `senddm` method.
    ```
    #api.destroy_direct_message(int(notifdm.id))
    ```
6. Makes a log for each run into `test.log` file.

## What do you need
1. Make sure you have already installed Python.
2. A Twitter developer account; sign in to your Twitter account then apply for a developer account <a href="https://developer.twitter.com/en/apply-for-access">here</a>. The time required until your application is approved might varies (mine was 10-14 days :grimacing:). After your application is approved, make sure to change the permission to the "Read, Write, and Direct Messages". Generate the keys and tokens after you change the permission setting.

## How to run this
1. If you have git installed, clone this in your directory. If not, just download the ZIP file.
    ```
    git clone https://github.com/azukacchi/twitter_autobase.git
    ```
2. Install the required packages (or check `requirements.txt` to install each package separately).
    ```
    pip install -r requirements.txt
    ```
3. Set the required fields in `config.py`:
    - Put the keys and tokens you get from your Twitter developer account.
    - Set your timezone and the trigger word you want to use.
4. Modify the notification message as you wish in the `senddm()` method.

## How do I automate the script
You can use Task Scheduler on Windows (open Start then search Task Scheduler) to run the `app.py`. This app is quite simple to use, the only downturn is it only runs when your computer is either turned on or sleep but not shutdown (obviously). Some helpful tutorials can be found [here](https://www.jcchouinard.com/python-automation-using-task-scheduler/) and [here](https://dev.to/abautista/automate-a-python-script-with-task-scheduler-3fb6).

## Notes
This bot is not suitable for a big autobase account. The `checkdm()` method only checks the DM to your bot account, without saving the tweets to a dabatase. Then this bot will post the incoming DM as soon as it runs the `post_all()` method, with a certain time span between the tweets to avoid Twitter API rate limits. To run a big autobase account with higher posts rate, coming from higher followers counts, such as [@collegemenfess](https://twitter.com/collegemenfess) with 500K+ followers, you'll need to check the dm more often and you'll need a database that enables you to store the incoming DM and post them later.

## Update 2020-12-02
For some reason, you cannot run this bot when you're connected to VPN. You won't be able to initiate `TwitterBot()` and it will give out errors such as `socket.timeout: The read operation timed out`.

## Questions
I've just started this as a new hobby during this pandemic, if you have any questions feel free to reach me on Twitter ahah :relaxed:
