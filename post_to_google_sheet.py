import network, utime
import prequests

#set login constants
def send_to_sheet(ssid, password, gKey, gSheetKey, data):
    '''
    Posts data to a google sheet using a google script.

        Parameters
        ----------
        ssid: string
            Network SSID
        password: string
            Network password
        gKey: string
            Google script app deployment ID, available when app is deployed. 
        gSheetKey: string
            API Key for Google Sheet. Available in sheet URL.
        sensor_readings: dictionary
            JSON string of data. Example format: {"Count":float(count),"Temp":float(temp),"Voltage":float(voltage)}
    Example
    -------
    >>> import direct_to_google_sheet
    >>> ssid = "YourSSID"
    >>> password ="YourPassword"
    >>> gKey = "YourgKey"
    >>> gSheetKey = "YourGSheetKey"
    >>> d1 = 121
    >>> d2 = 232
    >>> d3 = 434
    >>> data = {"Data1":float(d1),"Data2":float(d2),"Data3":float(d3)}
    >>> direct_to_google_sheet.send_to_sheet(ssid, password, gKey, gSheetKey, data)
    
    Notes
    -----
    Requires prequests (at https://gist.github.com/SpotlightKid/8637c685626b334e5c0ec341dd269c44
    (or uses erroneous urequests, but request is not returned because
    of Google API redirect).

    The following gooogle script must be pasted into a new
    Google script.  Then the script must be deployed as a web app
    for "Who has access" is "Anyone".

    function doPost(d) {
      //const SHEET_ID = "1AIWnPTtGNdlZ1TfbzpGTnheCOrPnKUHLUVefa8i2Y8k";
      const TIME_ZONE = "GMT+7";
      const TITLE = ["When","Patm(mbar)","Tatm(C)","PH20(mbar)","TH20(C)","Depth(m)","Battery(V)"]

      try {
        //var ss = SpreadsheetApp.openById(SHEET_ID);
        //var sheet = ss.getSheets()[0]                     // Use first Sheet in WorkSheet
        var data  = JSON.parse(d.postData.contents);

        if (data == undefined) {
          return ContentService.createTextOutput("GSheetApp ERROR!\r\nWrong parameters!");
        } else {
          var ss = SpreadsheetApp.openById(data.Sheet_id);
          var sheet = ss.getSheets()[0]                     // Use first Sheet in WorkSheet

          var row = sheet.getLastRow() + 1;

          if (row == 1) {                     // append TITLE at first row if Sheet empty
            sheet.appendRow(TITLE)
            row += 1 
          }
          
          sheet.getRange(row, 1).setValue(Utilities.formatDate(new Date(), TIME_ZONE, "dd.MM.yyyy HH:mm:ss"));
          sheet.getRange(row, 2).setValue(data.Patm || "no data");
          sheet.getRange(row, 3).setValue(data.Tatm || "no data");
          sheet.getRange(row, 4).setValue(data.PH20 || "no data");
          sheet.getRange(row, 5).setValue(data.TH20 || "no data");
          sheet.getRange(row, 6).setValue(data.Depth || "no data");    
          sheet.getRange(row, 7).setValue(data.Battery || "no data");          
          SpreadsheetApp.flush();
          
          if (data.mail !== undefined) {                    // Check Mail
            if (mail( data.mail, "Google Sheet msg", d.postData.contents) == false) {
              return ContentService.createTextOutput("GMailApp ERROR!\r\n" + e.message);
            }
          }  
          //appendData(data);                                // Save data to GSheet/GSheet.csv file
          return ContentService.createTextOutput("OK");
        }
      } catch(e) {
        return ContentService.createTextOutput("GSheetApp ERROR!\r\n" + e.message);
      }
    }
    '''
    
    try:
        sta_if = network.WLAN(network.STA_IF) #define object to access station mode functions
        sta_if.active(True) #make station mode active
        sta_if.connect(ssid, password)
        print('connected')
    except:
        print('not connected')
        pass

    #add sheet id to dictionary
    data['Sheet_id'] = gSheetKey

    #post to google sheet
    url = 'https://script.google.com/macros/s/'+gKey+'/exec'

    #The prequests library only works after an appropriate delay.
    #We don't want to delay more than necessary, so try and if it doesn't
    #work, delay and retry.  Repeat a few times.  
    for n in range(4):
        try:
            #print('trying request n = ',n)
            request = prequests.post(url, json = data)
            #request = urequests.post(url, json = data)
            utime.sleep(1)
            #print('posted, with following reason returned')
            #print(request.reason)
            outcome = ('Posted with reason: ',request.reason)
            request.close()
            break
        except Exception as e:
            print('error message')
            utime.sleep(1)
            if isinstance(e, OSError):
                try:
                    request.close()
                except:
                    print('request did not exist when closing')
            outcome = 'Post failed'
    return(outcome)
    
