# LatestPositions.vue Documentation 📄

*Display the latest positions of players on a map using Vue.js.*

---

## Table of Contents

- [Overview](#overview)
- [Component Structure](#component-structure)
  - [Template](#template)
  - [Script](#script)
    - [Props](#props)
    - [Data](#data)
    - [Computed Properties](#computed-properties)
    - [Watchers](#watchers)
    - [Methods](#methods)
    - [Lifecycle Hooks](#lifecycle-hooks)
- [Functionalities](#functionalities)
- [Usage](#usage)

---

## Overview

The **LatestPositions.vue** component is a Vue.js component designed to display the latest positions of players or objects on a map. It leverages the HTML5 `<canvas>` element to draw an image (the map) and overlay positions, paths, and directional arrows representing movement and orientation.

✨ **Key Features:**

- Displays a map image and overlays player positions.
- Draws paths showing the movement history.
- Shows direction with arrows based on rotation data.
- Dynamically updates when new position data is received.

---

## Component Structure

### Template

```html
<template>
  <div>
    <canvas ref="mapCanvas"></canvas>
  </div>
</template>
```

- The template consists of a single `<canvas>` element wrapped in a `<div>`.
- The `ref="mapCanvas"` allows for direct manipulation of the canvas in the script section.

---

### Script

```javascript
<script>
export default {
  name: 'latestpositions',
  // ...
}
</script>
```

#### Props

The component accepts several props to customize its behavior and display:

| Prop Name    | Type     | Required | Default | Description                                                                                  |
| ------------ | -------- | -------- | ------- | -------------------------------------------------------------------------------------------- |
| `positions`  | `Array`  | Yes      | `[]`    | Array of position data to display on the map.                                                |
| `mapUrl`     | `String` | Yes      |         | URL of the map image to display as the background.                                           |
| `realWidth`  | `Number` | Yes      |         | Real-world width of the map (used for scaling).                                              |
| `realHeight` | `Number` | Yes      |         | Real-world height of the map (used for scaling).                                             |
| `maxWidth`   | `Number` | No       | `500`   | Maximum width of the canvas.                                                                 |
| `maxHeight`  | `Number` | No       | `500`   | Maximum height of the canvas.                                                                |
| `offsetX`    | `Number` | No       | `0`     | X-axis offset for positioning.                                                               |
| `offsetY`    | `Number` | No       | `0`     | Y-axis offset for positioning.                                                               |
| `offsetRot`  | `Number` | No       | `0`     | Rotation offset (in degrees) to adjust the orientation of arrows representing direction.     |

**Example Props Usage:**

```javascript
props: {
  positions: {
    type: Array,
    required: true,
    default: () => []
  },
  mapUrl: {
    type: String,
    required: true
  },
  // other props...
}
```

#### Data

The component's data function returns:

- `img`: The Image object for the map.
- `imgWidth`: The calculated width of the map image.
- `imgHeight`: The calculated height of the map image.
- `scaleX`: Scaling factor for the X-axis.
- `scaleY`: Scaling factor for the Y-axis.

```javascript
data() {
  return {
    img: null,
    imgWidth: 0,
    imgHeight: 0,
    scaleX: 1,
    scaleY: 1
  };
}
```

#### Computed Properties

##### `groupedPositions`

- Groups the positions by their `index` property.
- Useful for handling multiple players or objects.

```javascript
computed: {
  groupedPositions() {
    return this.positions.reduce((groups, positionArray) => {
      positionArray.forEach((position) => {
        const index = position.index;
        if (!groups[index]) {
          groups[index] = [];
        }
        groups[index].push(position);
      });
      return groups;
    }, {});
  }
}
```

#### Watchers

The component watches for changes in:

- `positions`: To update and redraw positions when new data arrives.
- `mapUrl`: To update the map image when the URL changes.

```javascript
watch: {
  positions: {
    immediate: true,
    handler(newPositions) {
      if (newPositions.length > 0) {
        this.updateLatestPositions(newPositions);
      }
    }
  },
  mapUrl: {
    immediate: true,
    handler(newMapUrl) {
      if (this.img && newMapUrl !== this.img.src) {
        this.img.src = newMapUrl;
        this.setMap();
      }
    }
  }
}
```

#### Methods

The component defines several methods to handle drawing and updating the map and positions.

1. **`drawMap(ctx, canvas)`**

   - Draws the map image onto the canvas.
   - Resizes the image based on calculated dimensions.

   ```javascript
   drawMap(ctx, canvas) {
     if (this.img) {
       ctx.drawImage(this.img, 0, 0, this.imgWidth, this.imgHeight);
     }
   }
   ```

2. **`updateLatestPositions(newPositions)`**

   - Called when positions data changes.
   - Redraws the map and overlays the positions.

   ```javascript
   updateLatestPositions(newPositions) {
     this.$nextTick(() => {
       const canvas = this.$refs.mapCanvas;
       const ctx = canvas.getContext('2d');
       this.drawMap(ctx, canvas);
       this.drawPositions(ctx, newPositions, canvas);
     });
   }
   ```

3. **`drawPositions(ctx, newPositions, canvas)`**

   - Draws paths and positions on the map.
   - Handles multiple players by grouping positions.
   - Visualizes movement history and current position.

   ```javascript
   drawPositions(ctx, newPositions, canvas) {
     const mapCentreX = canvas.width / 2;
     const mapCentreY = canvas.height / 2;
     // Iterate through grouped positions
     for (const index in this.groupedPositions) {
       const playerPositions = this.groupedPositions[index];
       // Draw lines (paths)
       // Draw arrows and dots
     }
   }
   ```

4. **`drawArrowWithDot(ctx, posX, posY, rot, canvas, arrowLength, arrowWidth, color)`**

   - Draws an arrow representing direction and a dot at the current position.
   - Calculates the arrowhead based on rotation.

   ```javascript
   drawArrowWithDot(ctx, posX, posY, rot, canvas, arrowLength, arrowWidth, color) {
     // Calculate positions
     // Draw arrow line
     // Draw arrowhead
   }
   ```

5. **`setMap()`**

   - Loads the map image and sets up the canvas dimensions.
   - Calculates scaling factors based on the real-world dimensions.

   ```javascript
   setMap() {
     const canvas = this.$refs.mapCanvas;
     if (canvas) {
       this.img = new Image();
       this.img.src = this.mapUrl;
       this.img.onload = () => {
         const ctx = canvas.getContext('2d');
         // Calculate dimensions and scaling
         // Draw the map image onto the canvas
         this.drawMap(ctx, canvas);
       };
     }
   }
   ```

#### Lifecycle Hooks

##### `mounted`

- Called after the component is mounted.
- Initializes the map.

```javascript
mounted() {
  this.setMap();
}
```

---

## Functionalities

- **Map Rendering**: Displays a map image scaled to fit within specified maximum dimensions while maintaining aspect ratio.
- **Position Display**: Plots positions on the map, representing players or objects.
- **Path Drawing**: Draws lines (paths) showing the movement history of each player.
- **Direction Arrows**: Shows the orientation of players using arrows based on rotation data.
- **Dynamic Updates**: Automatically updates the display when new position data or a new map is received.
- **Scaling and Offsets**: Adjusts positions based on real-world dimensions and optional offsets to align the map correctly.

---

## Usage

To use the **LatestPositions.vue** component, you need to pass the required props:

```vue
<LatestPositions
  :positions="positionsData"
  :mapUrl="mapImageUrl"
  :realWidth="mapRealWidth"
  :realHeight="mapRealHeight"
  :maxWidth="800"
  :maxHeight="600"
  :offsetX="mapOffsetX"
  :offsetY="mapOffsetY"
  :offsetRot="mapRotationOffset"
/>
```

### Props Explanation

- **positionsData**: An array of position objects with the following structure:

  ```json
  [
    [
      {
        "index": 0,
        "posX": 10,
        "posZ": 20,
        "rotY": 45,
        "latestPositionColor": { "r": 255, "g": 0, "b": 0, "a": 1 },
        "olderPositionsColor": { "r": 255, "g": 165, "b": 0, "a": 0.8 },
        "pathColor": { "r": 255, "g": 165, "b": 0, "a": 0.6 }
      },
      // More positions...
    ],
    // More players...
  ]
  ```

- **mapImageUrl**: URL of the map image to display.
- **mapRealWidth** & **mapRealHeight**: Real-world dimensions of the map to scale positions accurately.
- **maxWidth** & **maxHeight**: Optional maximum dimensions for the canvas.
- **offsetX**, **offsetY**, **offsetRot**: Optional offsets to adjust positioning and rotation.
