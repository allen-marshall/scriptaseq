import QtQuick 2.9
import QtQuick.Controls 2.2

import ScriptASeq 0.1

ApplicationWindow {
  title: "ScriptASeq"
  color: "#000000"
  
  TimelineEditor {
    objectName: "editor"
    
    Rectangle {
      objectName: "bgRect"
      color: "#000040"
    }
    
    TimelineGrid {
      objectName: "grid"
    }
  }
}