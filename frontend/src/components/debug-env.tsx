import React from 'react';
import { Card } from '@/components/ui/card';
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export function DebugEnv() {
  const graphhopperKey = process.env.REACT_APP_GRAPHHOPPER_API_KEY;
  const datasfKey = process.env.REACT_APP_DATASF_API_KEY;
  
  const hasGraphhopper = graphhopperKey && graphhopperKey.length > 0;
  const hasDataSF = datasfKey && datasfKey.length > 0;
  
  // Only show in development or if there's an issue
  if (process.env.NODE_ENV === 'production' && hasGraphhopper) {
    return null;
  }
  
  return (
    <Card className="fixed bottom-4 right-4 p-4 max-w-sm shadow-lg border-2 bg-white/95 backdrop-blur z-50">
      <div className="flex items-center gap-2 mb-3">
        <AlertCircle className="h-5 w-5 text-yellow-500" />
        <h3 className="font-semibold">Environment Status</h3>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          {hasGraphhopper ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <XCircle className="h-4 w-4 text-red-500" />
          )}
          <span className="font-medium">GraphHopper API:</span>
          <span className={hasGraphhopper ? "text-green-600" : "text-red-600"}>
            {hasGraphhopper ? `✓ Configured (${graphhopperKey?.substring(0, 8)}...)` : '✗ Missing'}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {hasDataSF ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-500" />
          )}
          <span className="font-medium">DataSF API:</span>
          <span className={hasDataSF ? "text-green-600" : "text-yellow-600"}>
            {hasDataSF ? '✓ Configured' : '○ Optional'}
          </span>
        </div>
        
        <div className="pt-2 border-t text-xs text-gray-600">
          <p className="font-semibold text-red-600">⚠️ IMPORTANT: Exact naming required!</p>
          <ol className="mt-1 space-y-1">
            <li>1. Go to Vercel Dashboard → Settings</li>
            <li>2. Environment Variables</li>
            <li>3. <span className="font-bold">DELETE</span> any existing "GraphHopperAPI"</li>
            <li>4. Add NEW with EXACT name:</li>
            <li className="pl-3 font-mono font-bold">REACT_APP_GRAPHHOPPER_API_KEY</li>
            <li>5. Value: <span className="font-mono">ee6ac405-9a11-42e2-a0ac-dc333939f34b</span></li>
            <li>6. <span className="font-bold">Redeploy</span> after saving</li>
          </ol>
          <p className="mt-2 text-red-600 font-semibold">The name MUST start with REACT_APP_</p>
        </div>
      </div>
    </Card>
  );
}

export default DebugEnv;