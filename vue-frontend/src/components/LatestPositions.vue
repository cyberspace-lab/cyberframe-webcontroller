<template>
    <div>
      <canvas ref="mapCanvas"></canvas>
    </div>
  </template>
  
  <script>
  export default {
    name: 'latestpositions',
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
      realWidth: {
        type: Number,
        required: true
      },
      realHeight: {
        type: Number,
        required: true
      },
      maxWidth: {
        type: Number,
        default: 500
      },
      maxHeight: {
        type: Number,
        default: 500
      }
    },
    data() {
      return {
        img: null,
        imgWidth: 0,
        imgHeight: 0,
        scaleX: 1,
        scaleY: 1
      };
    },
    computed: {
      // Group the positions by index
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
    },
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
            this.setMap()
          }
        }
      }
    },
    methods: {
      // Load and draw the map (image) onto the canvas
      drawMap(ctx, canvas) {
        if (this.img) {
          // Draw the resized image on the canvas
          ctx.drawImage(this.img, 0, 0, this.imgWidth, this.imgHeight);
        }
      },
  
      // Update the positions and draw them on top of the map
      updateLatestPositions(newPositions) {
        this.$nextTick(() => {
          const canvas = this.$refs.mapCanvas;
          const ctx = canvas.getContext('2d');

          // First, draw the map once (only redraw the paths and positions over it)
          //this.img.src = this.mapUrl;
          this.drawMap(ctx, canvas);
  
          // Then draw the positions on top of the map
          this.drawPositions(ctx, newPositions, canvas);
        });
      },
  
      // Function to draw the positions (dots, arrows, etc.) on the canvas
      drawPositions(ctx, newPositions, canvas) {
        const mapCentreX = canvas.width / 2;
        const mapCentreY = canvas.height / 2;
  
        for (const index in this.groupedPositions) {
          const playerPositions = this.groupedPositions[index];

          // Draw all the lines first (in the original order)
          for (let i = 1; i < playerPositions.length; i++) {
            const position = playerPositions[i];
            const prevPosition = playerPositions[i - 1];
  
            const x = mapCentreX + (position.posX * this.scaleX);
            const y = mapCentreY + (-position.posZ * this.scaleY); // Flip the Y axis if needed

            const prevX = mapCentreX + (prevPosition.posX * this.scaleX);
            const prevY = mapCentreY + (-prevPosition.posZ * this.scaleY); // Flip the Y axis if needed
  
            // Adjust the line width based on the age of the position
            const lineWidth = Math.max(1, 5 - i * 0.4); // Line width decreases with age (limit to 1px)
  
            // Set the line width and draw the line
            ctx.lineWidth = lineWidth;
            ctx.beginPath();
            ctx.moveTo(prevX, prevY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = `rgba(${position.pathColor.r}, ${position.pathColor.g}, ${position.pathColor.b}, ${position.pathColor.a})`;
            ctx.stroke();
          }
  
          // Now draw all the arrows and dots in reverse order (starting from the last position)
          for (let i = playerPositions.length - 1; i >= 0; i--) {
            const position = playerPositions[i];
  
            // Skip if the current position is the same as the next one (same posX, posY, rotY)
            if (i > 0) {
              const nextPosition = playerPositions[i - 1];
              if (
                position.posX === nextPosition.posX &&
                position.posZ === nextPosition.posZ &&
                position.rotY === nextPosition.rotY
              ) {
                continue; // Skip drawing this position if it's the same as the next one
              }
            }
  
            const x = mapCentreX + (position.posX * this.scaleX);
            const y = mapCentreY + (-position.posZ * this.scaleY); // Flip the Y axis if needed
  
            // Calculate the dot and arrow size based on the position index (older positions are smaller)
            const dotSize = Math.max(2, 5 - i * 0.2); // Dot size decreases with age (limit to 2px)
            const arrowLength = Math.max(20, 30 - i * 2); // Arrow length decreases with age (limit to 20px)
            const arrowWidth = Math.max(6, 10 - i * 0.5); // Arrow width decreases with age (limit to 6px)
  
            // Draw the dot and arrow color based on the position (first is red, others are blue)
            const posColor = (i === 0) ? `rgba(${position.latestPositionColor.r}, ${position.latestPositionColor.g}, ${position.latestPositionColor.b}, ${position.latestPositionColor.a})` : `rgba(${position.olderPositionsColor.r}, ${position.olderPositionsColor.g}, ${position.olderPositionsColor.b}, ${position.olderPositionsColor.a})`;
            
            // Draw the dot
            ctx.beginPath();
            ctx.arc(x, y, dotSize, 0, 2 * Math.PI); // Dot with dynamic size
            ctx.fillStyle = posColor;
            ctx.fill();

            // Optionally, draw the arrow and rotation
            if (position.rotY !== undefined) {
              this.drawArrowWithDot(ctx, position.posX, position.posZ, position.rotY, canvas, arrowLength, arrowWidth, posColor);
            }
          }
        }
      },
  
      // Draw an arrow with a dot (you can modify this function as needed)
      drawArrowWithDot(ctx, posX, posY, rot, canvas, arrowLength, arrowWidth, color) {
        const mapCentreX = canvas.width / 2;
        const mapCentreY = canvas.height / 2;
  
        const x = mapCentreX + (posX * this.scaleX);
        const y = mapCentreY + (-posY * this.scaleY);
  
        const angle = rot * (Math.PI / 180); // Convert degrees to radians
  
        const endX = x + arrowLength * Math.cos(angle);
        const endY = y + arrowLength * Math.sin(angle);
  
        const leftX = endX + arrowWidth * Math.cos(angle + Math.PI * 5 / 6);
        const leftY = endY + arrowWidth * Math.sin(angle + Math.PI * 5 / 6);
        const rightX = endX + arrowWidth * Math.cos(angle - Math.PI * 5 / 6);
        const rightY = endY + arrowWidth * Math.sin(angle - Math.PI * 5 / 6);
  
        // Draw the arrow shaft
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(endX, endY);
        ctx.strokeStyle = color; // Arrow color (dynamic based on the position)
        ctx.lineWidth = 2;
        ctx.stroke();
  
        // Draw the arrowhead
        ctx.beginPath();
        ctx.moveTo(endX, endY);
        ctx.lineTo(leftX, leftY);
        ctx.lineTo(rightX, rightY);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
      },

      setMap() {
        const canvas = this.$refs.mapCanvas;
        if (canvas) {
          // Load the image once and store it in data
          this.img = new Image();
          this.img.src = this.mapUrl;
  
          // Once the image is loaded, calculate the dimensions
          this.img.onload = () => {
            const ctx = canvas.getContext('2d');
  
            // Get the natural width and height of the image
            const imgWidth = this.img.naturalWidth;
            const imgHeight = this.img.naturalHeight;
  
            // Calculate aspect ratio
            const aspectRatio = imgWidth / imgHeight;
  
            // Determine the new width and height to fit within the max width and height
            let newWidth = imgWidth;
            let newHeight = imgHeight;
  
            if (newWidth > this.maxWidth) {
              newWidth = this.maxWidth;
              newHeight = newWidth / aspectRatio;
            }
            if (newHeight > this.maxHeight) {
              newHeight = this.maxHeight;
              newWidth = newHeight * aspectRatio;
            }
  
            // Set canvas size to the resized image dimensions
            canvas.width = newWidth;
            canvas.height = newHeight;
  
            // Store the new width and height in data
            this.imgWidth = newWidth;
            this.imgHeight = newHeight;

            // Set the scaling factors based on the image size vs the real-world level size
            this.scaleX = newWidth / this.realWidth;
            this.scaleY = newHeight / this.realHeight;
  
            // Draw the resized image on the canvas
            this.drawMap(ctx, canvas);
          };
        }
      }
    },
    mounted() {
      this.setMap()
    }
  };
  </script>