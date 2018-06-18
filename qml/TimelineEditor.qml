import QtQuick 2.10

import ScriptASeq 0.1
        
TimelineEditor {
    
  Rectangle {
    objectName: "bgRect"
    color: "#000040"
  }
    
  TimelineGrid {
    objectName: "grid"
  }
          
  TimelineMarkers {
    objectName: "markers"
    
    Text {
      objectName: "markerTextH"
      visible: false
      color: "#ffff88"
      font.pointSize: 12
      x: 0
    }
            
    Text {
      objectName: "markerTextV"
      visible: false
      color: "#ffff88"
      font.pointSize: 12
      y: 0
    }
  }
}