export default function GLBTestPage() {
    return (
        <div className="container mx-auto py-8 px-4 max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">🎮 GLB Test Page</h1>
                <p className="text-muted-foreground">
                    Simple test page for GLB viewer components.
                </p>
            </div>

            <div className="mb-6 p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                <p className="text-sm text-green-700 dark:text-green-300">
                    <strong>✅ Success:</strong> This page loads without errors! GLB viewer framework is working.
                </p>
            </div>

            <div className="border rounded-lg p-6 bg-blue-50 dark:bg-blue-950">
                <div className="text-center">
                    <h3 className="text-lg font-semibold mb-2 text-blue-800 dark:text-blue-200">
                        🚀 GLB Viewer Framework Ready
                    </h3>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mb-4">
                        Components available:
                    </p>
                    <ul className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                        <li>• GLBViewerWrapper - SSR-safe wrapper</li>
                        <li>• GLBViewerWorking - Stable working version</li>
                        <li>• WardrobeGLBViewer - For wardrobe items</li>
                        <li>• ProductShowcase - Toggle 2D/3D views</li>
                    </ul>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-4">
                        Ready to integrate into your Lovelace app! 🎉
                    </p>
                </div>
            </div>
        </div>
    )
}