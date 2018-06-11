import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3

import ScriptASeq 0.1

ApplicationWindow {
  title: "ScriptASeq"
  color: "#000000"
  
  ColumnLayout {
    width: parent.width
    height: parent.height
  
    ScrollView {
      Layout.fillWidth: true
      Layout.fillHeight: true
      clip: true
    
      Flickable {
        boundsBehavior: Flickable.StopAtBounds
        
        TimelineEditor {
          objectName: "timelineEditor"
    
          Rectangle {
            objectName: "bgRect"
            color: "#000040"
          }
    
          TimelineGrid {
            objectName: "grid"
          }
          
          TimelineMarkers {
            objectName: "markers"
          }
        }
      }
    }
  }
}