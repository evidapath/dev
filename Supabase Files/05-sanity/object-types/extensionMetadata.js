// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.extension_metadata) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'extensionMetadata',
  title: 'Extension Metadata',
  type: 'object',
  fields: [
    defineField({
      name: 'note',
      title: 'Note',
      type: 'string',
    }),
    defineField({
      name: 'fields',
      title: 'Fields',
      type: 'array',
      of: [{ type: 'extensionMetadataFieldEntry' }], // free-form map -> deterministic key/value/value_type entries, never a stringified object
    }),
    defineField({
      name: 'proposed_v1_2_fields',
      title: 'Proposed V1 2 Fields',
      type: 'array',
      of: [{ type: 'string' }],
    }),
  ],
})
