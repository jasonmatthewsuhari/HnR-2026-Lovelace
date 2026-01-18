export default function GLBDemoPage() {
    return (
        <div className="container mx-auto py-8 px-4 max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">GLB 3D Model Viewer</h1>
                <p className="text-muted-foreground">
                    3D Model viewer demo page.
                </p>
            </div>

            <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                    <strong>Status:</strong> GLB viewer components are ready to use.
                </p>
            </div>

            <div className="grid gap-4">
                <div className="p-6 border rounded-lg">
                    <h2 className="text-lg font-semibold mb-2">Available Components</h2>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                        <li>GLBViewer - Main 3D viewer component</li>
                        <li>GLBViewerWrapper - SSR-safe wrapper</li>
                        <li>WardrobeGLBViewer - For wardrobe items</li>
                        <li>ProductShowcase - Toggle between 2D/3D views</li>
                        <li>VirtualTryOn - For try-on functionality</li>
                    </ul>
                </div>

                <div className="p-6 border rounded-lg">
                    <h2 className="text-lg font-semibold mb-2">Usage Example</h2>
                    <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded text-sm overflow-x-auto">
                        {`import { GLBViewerWrapper } from '@/components/glb-viewer-wrapper'

export function MyComponent() {
  return (
    <GLBViewerWrapper
      url="http://localhost:8000/3d/models/demo/product_3d.glb"
      height="400px"
      showAnimationControls={true}
      enableControls={true}
    />
  )
}`}
                    </pre>
                    <div className="mt-4">
                        <a
                            href="/glb-test"
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                        >
                            Try Live Demo →
                        </a>
                    </div>
                </div>

                <div className="p-6 border rounded-lg">
                    <h2 className="text-lg font-semibold mb-2">Backend Endpoints</h2>
                    <ul className="space-y-1 text-sm">
                        <li><code>GET /3d/models</code> - List all models</li>
                        <li><code>GET /3d/download/{'{model_id}'}</code> - Download model</li>
                        <li><code>POST /3d/generate</code> - Generate 3D from image</li>
                        <li><code>GET /3d/models/demo/product_3d.glb</code> - Demo model</li>
                    </ul>
                </div>
            </div>
        </div>
    )
}