// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.accepted_assessment) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'acceptedAssessment',
  title: 'Accepted Assessment',
  type: 'object',
  fields: [
    defineField({
      name: 'test_name',
      title: 'Test Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'necessity',
      title: 'Necessity',
      type: 'string',
      options: { list: ["required", "recommended", "optional"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'competitive_benchmark',
      title: 'Competitive Benchmark',
      type: 'string', // source field is string|number|null -- see validation-rules.md
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
    }),
  ],
})
