// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.monthly_range) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'monthlyRange',
  title: 'Monthly Range',
  type: 'object',
  fields: [
    defineField({
      name: 'min',
      title: 'Min',
      type: 'number',
    }),
    defineField({
      name: 'max',
      title: 'Max',
      type: 'number',
    }),
    defineField({
      name: 'currency',
      title: 'Currency',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
  ],
})
