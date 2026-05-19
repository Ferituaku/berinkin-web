'use client';

import { useEffect, useRef } from 'react';

interface Leaf {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  rotation: number;
  rotationSpeed: number;
  oscillationSpeed: number;
  oscillationPhase: number;
  color: string;
}

export default function FallingLeaves() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let leaves: Leaf[] = [];
    // Number of leaves based on screen width for better density
    const numLeaves = Math.min(Math.floor(window.innerWidth / 25), 50); 
    
    // Theme colors: primary-container, primary-fixed-dim, outline-variant, with some opacity
    const colors = [
      'rgba(6, 78, 59, 0.25)',   // primary-container
      'rgba(149, 211, 186, 0.4)', // primary-fixed-dim
      'rgba(191, 201, 195, 0.3)', // outline-variant
      'rgba(43, 105, 84, 0.2)'    // surface-tint
    ];

    const mouse = { x: -1000, y: -1000 };
    let mouseSpeed = 0;
    const lastMouse = { x: -1000, y: -1000 };

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const initLeaves = () => {
      leaves = [];
      for (let i = 0; i < numLeaves; i++) {
        leaves.push(createLeaf());
      }
    };

    const createLeaf = (resetY = false): Leaf => {
      return {
        x: Math.random() * canvas.width,
        y: resetY ? -20 : Math.random() * canvas.height,
        size: Math.random() * 6 + 4, // 4 to 10
        speedX: Math.random() * 1 - 0.5,
        speedY: Math.random() * 0.8 + 0.4, // 0.4 to 1.2
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.03,
        oscillationSpeed: Math.random() * 0.015 + 0.005,
        oscillationPhase: Math.random() * Math.PI * 2,
        color: colors[Math.floor(Math.random() * colors.length)]
      };
    };

    const drawLeaf = (ctx: CanvasRenderingContext2D, leaf: Leaf) => {
      ctx.save();
      ctx.translate(leaf.x, leaf.y);
      ctx.rotate(leaf.rotation);
      
      // Draw a beringin/banyan leaf shape
      ctx.beginPath();
      ctx.moveTo(0, -leaf.size);
      ctx.bezierCurveTo(leaf.size * 0.8, -leaf.size * 0.5, leaf.size * 0.8, leaf.size * 0.8, 0, leaf.size);
      ctx.bezierCurveTo(-leaf.size * 0.8, leaf.size * 0.8, -leaf.size * 0.8, -leaf.size * 0.5, 0, -leaf.size);
      ctx.fillStyle = leaf.color;
      ctx.fill();
      
      // Add a subtle stem/vein
      ctx.beginPath();
      ctx.moveTo(0, -leaf.size * 0.8);
      ctx.lineTo(0, leaf.size * 1.2);
      // Try to replace opacity dynamically, fallback if it fails
      const strokeColor = leaf.color.includes('rgba') 
        ? leaf.color.replace(/[\d.]+\)$/g, '0.5)') 
        : 'rgba(0,0,0,0.2)';
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 0.5;
      ctx.stroke();

      ctx.restore();
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Calculate mouse speed for dynamic interaction
      const dx = mouse.x - lastMouse.x;
      const dy = mouse.y - lastMouse.y;
      mouseSpeed = Math.sqrt(dx * dx + dy * dy);
      
      // Decay mouse speed gradually
      lastMouse.x += (mouse.x - lastMouse.x) * 0.1;
      lastMouse.y += (mouse.y - lastMouse.y) * 0.1;

      leaves.forEach((leaf) => {
        // Natural falling oscillation
        leaf.x += Math.sin(leaf.oscillationPhase) * 0.5 + leaf.speedX;
        leaf.y += leaf.speedY;
        leaf.rotation += leaf.rotationSpeed;
        leaf.oscillationPhase += leaf.oscillationSpeed;

        // Mouse interaction (repel)
        const distToMouseX = leaf.x - mouse.x;
        const distToMouseY = leaf.y - mouse.y;
        const distance = Math.sqrt(distToMouseX * distToMouseX + distToMouseY * distToMouseY);
        
        // Increase repel radius if moving fast
        const repelRadius = 120 + Math.min(mouseSpeed * 2, 100);

        if (distance < repelRadius) {
          const force = (repelRadius - distance) / repelRadius;
          // Apply force based on direction from mouse to leaf
          leaf.x += (distToMouseX / distance) * force * 3;
          leaf.y += (distToMouseY / distance) * force * 3;
          
          // Add some spin when hit
          leaf.rotationSpeed += (Math.random() - 0.5) * force * 0.05;
        }

        // Apply drag to return to normal speed after being hit by mouse
        leaf.rotationSpeed *= 0.98;
        if (Math.abs(leaf.rotationSpeed) < 0.01) {
          leaf.rotationSpeed = (Math.random() - 0.5) * 0.03; // Restore base rotation
        }

        // Reset if out of bounds (bottom or sides)
        if (leaf.y > canvas.height + 20 || leaf.x < -20 || leaf.x > canvas.width + 20) {
          Object.assign(leaf, createLeaf(true));
        }

        drawLeaf(ctx, leaf);
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    handleResize();
    initLeaves();
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      aria-hidden="true"
    />
  );
}
