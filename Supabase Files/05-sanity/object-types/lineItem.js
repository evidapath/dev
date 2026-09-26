// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.line_item) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'lineItem',
  title: 'Line Item',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'amount',
      title: 'Amount',
      type: 'number',
    }),
    defineField({
      name: 'frequency',
      title: 'Frequency',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
  ],
})
