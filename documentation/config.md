# 📄 Configuration File Documentation: `config.json`

---

## Table of Contents
1. [Introduction](#introduction)
2. [Overall Structure](#overall-structure)
3. [Applications](#applications)
   - [MoveDifferent](#movedifferent)
     - [Control Buttons](#movedifferent-control-buttons)
     - [Receivers](#movedifferent-receivers)
     - [Levels](#movedifferent-levels)
4. [Minimum Free Memory Percentage](#minimum-free-memory-percentage)
5. [Conclusion](#conclusion)

---

## Introduction

The `config.json` file is a critical configuration file for the application, providing customizable settings for different applications within the system. It defines control buttons, data receivers, levels, and memory management settings for each application. This allows for a flexible and dynamic configuration that can be adjusted without modifying the codebase.

---

## Overall Structure

The `config.json` file is structured as a JSON object with the following top-level keys:

- **applications**: An object containing configurations for each application.
- **min_free_memory_percentage**: An integer specifying the minimum percentage of free memory before triggering cleanup.

```json
{
  "applications": { ... },
  "min_free_memory_percentage": 20
}
```

---

## Applications

The **applications** key contains configurations for individual applications. In this file, there are two applications configured:

1. **Diplomovka**
2. **MoveDifferent**

Each application has the following configurable sections:

- **controlButtons**
- **receivers**
- **levels**

---

### MoveDifferent

#### **Control Buttons**

The **controlButtons** array defines interactive buttons that can send commands to the application. Each button has properties like:

- **title**: The text displayed on the button.
- **payload**: The data sent when the button is pressed.
  - **eventName**: The event to trigger in the application.
  - **parameters**: Additional parameters for the event.
- **requiresInput** *(optional)*: A boolean indicating if the button requires user input.
- **inputPlaceholder** *(optional)*: Placeholder text for the input field.

##### 📋 Button Definitions:

1. **Set participant name**
   - **Requires Input**: ✅
   - **Placeholder**: "Participant"
   - **Event**: `participantName`
   - **Context**: `["menu"]`

2. **Start Test Teleport**
   - **Event**: `startLevel`
   - **Parameters**: `{ "settingsIndex": 0 }`
   - **Context**: `["menu"]`

3. **Start Test Dash**
   - **Event**: `startLevel`
   - **Parameters**: `{ "settingsIndex": 1 }`
   - **Context**: `["menu"]`

4. **Start/Stop Experiment**
   - **Event**: `startStopExperiment`
   - **Context**: `["level"]`

5. **Go to menu**
   - **Event**: `goToMenu`
   - **Context**: `["level"]`

*(Additional buttons omitted for brevity)*

#### **Receivers**

The **receivers** array defines data keys that the application listens to, along with their history settings.

##### 📡 Receiver Definitions:

1. **currentScene**
   - **maxHistory**: 10

2. **location**
   - **maxHistory**: 20

3. **position**
   - **maxHistory**: 10

#### **Levels**

The **levels** array contains level configurations, each with specific attributes.

##### 🗺️ Level Definitions:

1. **Level 1**
   - **ID**: `1`
   - **URL**: *Dungeon map image link*
   - **Dimensions**: `realWidth`: 25.5, `realHeight`: 26.5
   - **Map Offsets**:
     - **mapOffsetX**: -0.7
     - **mapOffsetY**: 3.3
     - **mapOffsetRotation**: -90

2. **Level 2**
   - **ID**: `2`
   - **URL**: *Test map image link*
   - **Dimensions**: `realWidth`: 40, `realHeight`: 40

*(Additional levels omitted for brevity)*

---

## Minimum Free Memory Percentage

The **min_free_memory_percentage** key specifies the minimum percentage of free memory required before triggering memory cleanup processes.

```json
"min_free_memory_percentage": 20
```

- **Value**: `20`%
  - When the available system memory drops below 20%, the application will initiate cleanup routines to free up memory, ensuring optimal performance.

---

## Conclusion

The `config.json` file provides a flexible and detailed configuration setup for different applications within the system. By defining control buttons, data receivers, and level configurations, developers and administrators can easily tailor the application behavior without modifying the core code. The inclusion of memory management settings helps maintain system stability and performance.
