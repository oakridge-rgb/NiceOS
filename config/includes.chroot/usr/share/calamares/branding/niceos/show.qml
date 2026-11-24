import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation

    Timer {
        interval: 8000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Image {
            source: "slide-1.png"
            anchors.centerIn: parent
            width: parent.width * 0.9
            fillMode: Image.PreserveAspectFit
        }
    }

    Slide {
        Image {
            source: "slide-2.png"
            anchors.centerIn: parent
            width: parent.width * 0.9
            fillMode: Image.PreserveAspectFit
        }
    }
}
