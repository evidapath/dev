import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'
import {schemaTypes} from './schemaTypes'

export default defineConfig({
  name: 'default',
  title: 'evidapath',

  projectId: 'jxwrtsiz',
  dataset: 'staging',

  plugins: [structureTool(), visionTool()],

  schema: {
    types: schemaTypes,
  },
})
