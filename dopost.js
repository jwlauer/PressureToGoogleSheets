//This app must be set up in a Google App Scripts account and deployed. Once deployed, copy the API key 
//and paste into the micropython code.

function doPost(d) {
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
