// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.selection_criterion) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'selectionCriterion',
  title: 'Selection Criterion',
  type: 'object',
  fields: [
    defineField({
      name: 'criterion_name',
      title: 'Criterion Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'threshold_or_formula',
      title: 'Threshold Or Formula',
      type: 'string',
    }),
    defineField({
      name: 'weight',
      title: 'Weight',
      type: 'string', // source field is string|number|null -- see validation-rules.md
    }),
    defineField({
      name: 'mandatory',
      title: 'Mandatory',
      type: 'boolean',
      validation: (Rule) => Rule.required(),
    }),
  ],
})
