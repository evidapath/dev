// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.testing_policy) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'testingPolicy',
  title: 'Testing Policy',
  type: 'object',
  fields: [
    defineField({
      name: 'policy_type',
      title: 'Policy Type',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'accepted_assessments',
      title: 'Accepted Assessments',
      type: 'array',
      of: [{ type: 'acceptedAssessment' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'scope_note',
      title: 'Scope Note',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
    }),
  ],
})
