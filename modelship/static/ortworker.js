import * as ort from './vendor/onnxruntime-web/ort.bundle.min.js'

console.info(`[worker] onnxruntime-web version: ${ort.env.versions.web}`)

// monkeypatch self.postMessage to log to the console at debug level
const originalPostMessage = self.postMessage.bind(self)
self.postMessage = (msg) => {
  console.debug('[worker →]', msg)
  originalPostMessage(msg)
}

// permanent onnx runtime inference session
let session

async function init(modelPath) {
  const sessionOption = { executionProviders: ['webgpu', 'wasm'] }
  console.debug(`[worker] initializing onnxruntime-web inference session`)
  console.debug(`[worker]   model path: ${modelPath}`)
  console.debug(`[worker]   session options: ${JSON.stringify(sessionOption, null, 4)}`)
  session = await ort.InferenceSession.create(modelPath, sessionOption)
}

async function predict(modelMetadata, inputs) {
  console.debug('[worker] performing model inference with onnxruntime-web inference session')
  console.debug(`[worker]   metadata: ${JSON.stringify(modelMetadata, null, 4)}`)
  console.debug(`[worker]   inputs: ${JSON.stringify(inputs, null, 4)}`)

  const inputTensors = {}
  for (const [key, value] of Object.entries(inputs)) {
    const metadata = modelMetadata.inputs[key]
    const shape = metadata.shape.map(item => item === null ? 1 : item)
    const array = (metadata.type === 'float32') ? Float32Array.from([value]) : [value]
    inputTensors[key] = new ort.Tensor(metadata.type, array, shape)
  }

  const results = await session.run(inputTensors)
  const outputs = Object.fromEntries(
    Object.entries(results).map(([key, value]) => [key, Array.from(value.data)])
  )
  console.debug(`[worker]   outputs: ${JSON.stringify(outputs, null, 4)}`)

  return outputs
}

// worker message handling
self.onmessage = async function (e) {
  const { type, payload } = e.data
  console.debug(`[→ worker] onmessage: type=${type}`)

  switch (type) {
    case 'load':
      try {
        await init(payload.modelPath)
        self.postMessage({ type: 'load-success' })
      } catch (error) {
        self.postMessage({ type: 'load-error', error: error.message || String(error) })
      }
      break

    case 'predict':
      try {
        const outputs = await predict(payload.modelMetadata, payload.inputs)
        self.postMessage({ type: 'predict-success', outputs })
      } catch (error) {
        self.postMessage({ type: 'predict-error', error: error.message || String(error) })
      }
      break
  }
}

// signal worker is ready
self.postMessage({ type: 'ready' })
