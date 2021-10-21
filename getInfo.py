#Count execution time
from datetime import datetime
startTime = datetime.now()
#Imports
import urllib
import requests
import sys
import subprocess
import os
import jq
from PIL import Image, ImageDraw, ImageFont, ImageFilter

#Load list of profiles from twitchList
pathToScript='/home/pi/twitchinfo/'
f = open(pathToScript+'twitchList','r')
detailedList = open(pathToScript+'detailedList','w+')
for line in f:
#Getting twitch name from argument
#######################TODO: Read from twitchList
    twitchNick=line[:-1]

#Getting data from twitch API (first URL)
    url = "https://api.twitch.tv/helix/users?login="+twitchNick
    headers = {'Authorization': 'Bearer 0q48fulnd4pzwyd15vhttkd3yxhkvq', 'Client-Id': 'cas1rh4vb47dxuvidt5ocgawepfd4z'}

#Save data (first URL)
    r = str(requests.get(url, headers=headers).content)[2:-1]
    r=r.replace("\\","")
    f = open(pathToScript+"temp.file","w")
    f.write(str(r))
    f.close()

#Getting stuff from first URL
    twitchId = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' . | .data[] | .id'", shell=True)
    twitchId = str(twitchId)[3:-4]
    twitchName = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' . | .data[] | .display_name'", shell=True)
    twitchName = str(twitchName)[3:-4]
    twitchImage = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' . | .data[] | .profile_image_url'", shell=True)
    twitchImage = str(twitchImage)[3:-4]
    twitchCreated = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' . | .data[] | .created_at'", shell=True)
    twitchCreated = str(twitchCreated)[3:-4].split("T")[0]
    twitchViews = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' . | .data[] | .view_count'", shell=True)
    twitchViews = str(twitchViews)[2:-3]

#Second URL
    url = "https://api.twitch.tv/helix/users/follows?to_id="+twitchId

#Save data (second URL)
    r = str(requests.get(url, headers=headers).content)[2:-1]
    r = r.replace("\\","")
    f = open(pathToScript+"temp.file","w")
    f.write(str(r))
    f.close()

#Get stuff from second URL
    twitchFollowers = subprocess.check_output("cat "+pathToScript+"temp.file | jq ' .total '", shell=True) 
    twitchFollowers = str(twitchFollowers)[2:-3]

    print("Twitch ID: "+twitchId)
    print("Twitch name: "+twitchName)
    print("Twitch pic: "+twitchImage)
    print("Twitch followers: "+twitchFollowers)
    print("Twitch created at: "+twitchCreated)
    print("Twitch views: "+twitchViews)
    print("----------------------------")
    detailedList.write(twitchId+";"+twitchName+";"+twitchImage+";"+twitchFollowers+";"+twitchCreated+";"+twitchViews+"\n")
################################
# Image creation
#################################
detailedList.close()
pathToScript='/home/pi/twitchinfo/'
detailedList = open(pathToScript+'detailedList')
img = Image.open(pathToScript+'background528x405.png')
img = img.convert("RGB")
smallfnt = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf',11)
nameFont = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf',14)
longNameFont = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf',12)
dateFont = ImageFont.truetype(pathToScript+'ShareTechMono-Regular.ttf',12)
emblem = Image.open(pathToScript+'emblem113x173.png')
emblem = emblem.convert("RGBA")
imgDraw = ImageDraw.Draw(img,'RGBA')
emblemIndex = 0
lineIndex = 0
for line in detailedList:
    twitchName = line.split(";")[1]
    twitchImage = line.split(";")[2]
    twitchFollowers = line.split(";")[3]
    twitchCreated = line.split(";")[4]
    twitchViews = line.split(";")[5]
    savedImageFile = urllib.request.urlretrieve(twitchImage, pathToScript+"twitchpic.png")
    twitchPicFile = Image.open(pathToScript+"twitchpic.png")
    twitchPicFile = twitchPicFile.convert("RGBA")
    avatarBorderFile = Image.open(pathToScript+"avatarBorder113x113.png")
    avatarBorderFile = avatarBorderFile.convert("RGBA")
    twitchPicFileResized = twitchPicFile.resize((80,80))
    twitchPicFileResized.save(pathToScript+'twitchpicresized.png')
    twitchPicFileResized = Image.open(pathToScript+"twitchpicresized.png")
    twitchPicMask = Image.open(pathToScript+"maskForAvatar.png")
    preparedImage = Image.new("RGBA", twitchPicFileResized.size, 0)
    preparedImage.paste(twitchPicFileResized, (0,0), twitchPicFileResized)
    #print("Adding emblem - index: "+str(emblemIndex)+" lineIndex: "+str(lineIndex)+"\n")
    baseLocationX = 10+(113+15)*emblemIndex
    baseLocationY = 20+(173+15)*lineIndex
    img.paste(emblem, (baseLocationX, baseLocationY), emblem)
    img.paste(avatarBorderFile, (baseLocationX - 3, baseLocationY), avatarBorderFile)
    img.paste(preparedImage, (baseLocationX + 14, baseLocationY+15), twitchPicMask)
    # middleLocationX = 56
    # centeredLocation = int(56 - (len(twitchName) * 4))
    if len(twitchName) < 15:
        centeredLocation = int(56 - (len(twitchName) * 4))
        imgDraw.text((baseLocationX + centeredLocation, baseLocationY + 100), twitchName, font=nameFont, fill=(255,255,255))
    else:
        centeredLocation = int(56 - (len(twitchName) * 3))
        imgDraw.text((baseLocationX + centeredLocation, baseLocationY + 102), twitchName, font=longNameFont, fill=(255,255,255))
    imgDraw.text((baseLocationX + 15, baseLocationY + 117), twitchFollowers, font=nameFont, fill=(255,255,255))
    imgDraw.text((baseLocationX + 15, baseLocationY + 133), twitchViews, font=nameFont, fill=(255,255,255))
    imgDraw.text((baseLocationX + 43, baseLocationY + 150), twitchCreated, font=dateFont, fill=(255,255,255))


    emblemIndex += 1
    #Move to a new line every 4 emblems
    if (emblemIndex % 4) == 0: 
        lineIndex += 1
        emblemIndex = 0

executionTime=str(round(datetime.now().timestamp() - startTime.timestamp(),2))
print("EX:"+executionTime+" NOW:"+str(datetime.now()))
imgDraw.text((0,390), "Generated in ~"+str(executionTime)+" seconds by qBot on "+str(datetime.now())[0:-7]+". Long live Slav Squat Squad!", font=smallfnt, fill=(20,20,20))
img.save(pathToScript+'twitchInfo.png', quality=95)
