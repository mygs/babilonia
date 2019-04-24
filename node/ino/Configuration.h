#ifndef __CONFIGURATION_H
#define __CONFIGURATION_H

struct Configuration {
        char* SSID;
        char* PASSWORD;
        char* MQTT_SERVER;
        int MQTT_PORT;
        char* MQTT_TOPIC_INBOUND;
        char* MQTT_TOPIC_OUTBOUND;
};
#endif // ifndef __CONFIGURATION_H
