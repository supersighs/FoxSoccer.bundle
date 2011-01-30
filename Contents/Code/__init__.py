# PMS plugin frameworks
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/foxsoccer"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ARTWORK       = 'art.png'
ICON          = 'icon-default.png'
FOX_BASE      = 'http://www.beta.foxsoccer.tv'
WATCH_LIVE    = 'http://www.beta.foxsoccer.tv/page/WatchLive'
FULL_SCHEDULE = 'http://www.beta.foxsoccer.tv/page/LiveSchedule'
REPLAY        = 'http://www.beta.foxsoccer.tv/page/CatchUp'
AUTH_URL      = 'https://secure-foxsoccer.premiumtv.co.uk/internalLogin/loginProcess'

####################################################################################################

def Start():
    HTTP.__headers["User-agent"] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-gb) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16"
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'),ICON)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
   # MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    #DirectoryItem.thumb = R(ICON)

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Video' prefix handler
#

def VideoMainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="InfoList")
    dir.Append(Function(DirectoryItem(VideoPage, "Live Games"), pageUrl = WATCH_LIVE ))
    dir.Append(Function(DirectoryItem(VideoPage, "Full Schedule"), pageUrl = FULL_SCHEDULE ))
    dir.Append(Function(DirectoryItem(VideoPage, "Replay"), pageUrl = REPLAY ))
    
    dir.Append(PrefsItem(L("Preferences")))
    

    # see:
    #  http://dev.plexapp.com/docs/Objects.html#DirectoryItem
    #  http://dev.plexapp.com/docs/Objects.html#function-objects


    # ... and then return the container
    return dir

def CreatePrefs():
    Prefs.Add('login',type='text',default='',label='FoxSoccer Login')
    Prefs.Add('password',type='text',default='',label='FoxSoccer Password', option='hidden')
    
def GetAuthenticatedLivePage(pageUrl):
    attempt_page_content = XML.ElementFromURL(pageUrl, isHTML=True)
    if len(attempt_page_content.xpath("//div[contains(@class,'teaserArticle')]")) > 0:
        Log(Prefs.get("login"))
        Log(Prefs.get("password"))
        auth = HTTP.Request(AUTH_URL,values = { "target":"http://www.beta.foxsoccer.tv/page/CatchUp","redirectPage":"","userName":Prefs.Get("login"),"password":Prefs.Get("password")})
    return XML.ElementFromURL("http://www.beta.foxsoccer.tv/page/elements/html/Home/0,,13138~226~10483,00.html", isHTML=True)

def VideoPage(sender,pageUrl):

    ## you might want to try making me return a MediaContainer
    ## containing a list of DirectoryItems to see what happens =)
    
    # always need to request page
    
    if "WatchLive" in pageUrl:
        # Need to authenticate to view this page correctly
        Log("Picked Live")
        page_content = GetAuthenticatedLivePage(pageUrl)
        dir = MediaContainer(title2 = sender.itemTitle, viewGroup = "List")
        games = page_content.xpath("//div[@class='liveEvent']|//div[@class='liveEvent remMargin']")
        for event in games:
            teamOne = event.xpath("./div[@class='liveEventTop']/div[@class='liveEventTeamNames']/div[@class='liveEventTeamOne watchLiveTeams']")[0].text
            teamTwo = event.xpath("./div[@class='liveEventTop']/div[@class='liveEventTeamNames']/div[@class='liveEventTeamTwo watchLiveTeams']")[0].text
            eventTime = event.xpath("./div[@class='liveEventBottom']/div[@class='liveEventTime']")[0].text
            liveCheck = event.xpath("./div[@class='liveEventBottom']/div[@class='isItLive']/div/div[@class='buttonMiddle']/a/@href")
            if len(liveCheck) < 1:
                eventLink = "Coming up soon"
            else:
                eventLink = liveCheck[0]
            eventTitle = teamOne + " vs. " + teamTwo + " @ " + eventTime
            if "Coming" in eventLink:
                dir.Append(WebVideoItem(url="",title = eventTitle + "(" + eventLink + ")"))
            else:
                dir.Append(WebVideoItem(url= FOX_BASE + eventLink,title = eventTitle + "(Live Now)"))
    if "LiveSchedule" in pageUrl:
        page_content =XML.ElementFromURL(pageUrl, isHTML=True)
        dir = MediaContainer(viewGroup = "InfoList")
        dates = page_content.xpath("//div[@class='results']/div/div[@class='eventGroupinner']/h1/text()")
        for date in dates:
            dir.Append(Function(DirectoryItem(DayPage,date)))
                
    if "CatchUp" in pageUrl:
        dir = MediaContainer(viewGroup = "InfoList")
        dir.Append(Function(DirectoryItem(ReplayPage, "Full Matches")))
        dir.Append(Function(DirectoryItem(ReplayPage, "45 Minute Highlights")))
        dir.Append(Function(DirectoryItem(ReplayPage, "Free Highlights")))
        dir.Append(Function(DirectoryItem(ReplayPage, "Features")))
        
    return dir
        
        #//div[contains(@class,'45minTab')]
def DayPage(sender):
    dir = MediaContainer(title2 = sender.itemTitle, viewGroup = "List")
    page_content = XML.ElementFromURL(FULL_SCHEDULE, isHTML=True)
    parent_div = page_content.xpath("//h1[text() = '" + sender.itemTitle + "' ]/..")[0]
    games = parent_div.xpath("./table/tbody/tr")
    for game in games:
        teams_arr = game.xpath("./td[@class='team']/text()")
        Log(len(teams_arr))
        game_title = teams_arr[0] + " vs. " + teams_arr[1]
        league = game.xpath("./td[@class='comp']/text()")[0]
        kickoff_check = game.xpath("./td[@class='kotime']/text()")
        if len(kickoff_check) > 0:
            kickoff = kickoff_check[0]
        else:
            kickoff = "N/A"
        liveCheck = game.xpath("./td[@class='coverage']/a/@href")
        if len(liveCheck) < 1:
            coverageCheck = game.xpath("./td[@class='coverage']/text()")
            if len(coverageCheck) < 1:
                coverage = "On Demand: " + game.xpath("./td[@class='onDemand']/span/text()")[0]
            else:
                coverage = coverageCheck[0]
            dir.Append(WebVideoItem(url="",title = game_title, summary = league + " - Kickoff: " + kickoff + " - Coverage: " + coverage))
        else:
            dir.Append(WebVideoItem(url= liveCheck[0],title = game_title, summary = league + " - Started at " + kickoff))
    
    return dir
        
def ReplayPage(sender):
    
    dir = MediaContainer(title2 = sender.itemTitle, viewGroup = "List")
    page_content = XML.ElementFromURL(REPLAY, isHTML=True)
    if "Full" in sender.itemTitle:
        full_games = page_content.xpath("//div[contains(@class,'FullMatchTab')]/div[@class='videoSearch']/div/div/div[contains(@class,'video')]")
        for event in full_games:
           game_title = event.xpath("./div[@class='teaser']/div[@class='title']/@title")[0]
           img_link = FOX_BASE + event.xpath("./div[@class='videoTeaser']/a/img/@src")[0]
           video_url = event.xpath("./div[@class='videoTeaser']/a/@href")[0]
           dir.Append(WebVideoItem(url=video_url,title = game_title,thumb = img_link))
    elif "45" in sender.itemTitle:
        fvmin_games = page_content.xpath("//div[contains(@class,'45minTab')]/div/div/div[@class='results']/div[contains(@class,'video')]")
        for event in fvmin_games:
            game_title = event.xpath("./div[@class='teaser']/div[@class='title']/a/text()")[0]
            img_link = FOX_BASE + event.xpath("./div[@class='videoTeaser']/a/img/@src")[0]
            video_url = FOX_BASE + event.xpath("./div[@class='teaser']/div[@class='title']/a/@href")[0]
            sum_data = event.xpath("./div[@class='teaser']/div[@class='date']/text()")
            sub = sum_data[1] + "(" + sum_data[3] + ")"
            dir.Append(WebVideoItem(url=video_url,title = game_title,thumb = img_link, subtitle = sub))
    elif "Free" in sender.itemTitle:
        free_games = page_content.xpath("//div[contains(@class,'FreeHighlightsTab')]/div/div/div[@class='results']/div[contains(@class,'video')]")
        for event in free_games:
            game_title = event.xpath("./div[@class='teaser']/div[@class='title']/a/text()")[0]
            img_link = FOX_BASE + event.xpath("./div[@class='videoTeaser']/a/img/@src")[0]
            video_url = FOX_BASE + event.xpath("./div[@class='teaser']/div[@class='title']/a/@href")[0]
            sum_data = event.xpath("./div[@class='teaser']/div[@class='date']/text()")
            sub = sum_data[1] + "(" + sum_data[3] + ")"
            dir.Append(WebVideoItem(url=video_url,title = game_title,thumb = img_link, subtitle = sub))
    elif "Features" in sender.itemTitle:
        free_games = page_content.xpath("//div[contains(@class,'ClassicTab')]/div/div/div[@class='results']/div[contains(@class,'video')]")
        for event in free_games:
            game_title = event.xpath("./div[@class='teaser']/div[@class='title']/@title")[0]
            img_link = FOX_BASE + event.xpath("./div[@class='videoTeaser']/a/img/@src")[0]
            video_url = FOX_BASE + event.xpath("./div[@class='teaser']/div[@class='title']/a/@href")[0]
            sum_data = event.xpath("./div[@class='teaser']/div[@class='date']/text()")
            sub = sum_data[1] + "(" + sum_data[3] + ")"
            dir.Append(WebVideoItem(url=video_url,title = game_title,thumb = img_link, subtitle = sub))
            
    return dir
          
        

  
