// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.progression_requirement) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'progressionRequirement',
  title: 'Progression Requirement',
  type: 'object',
  fields: [
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'gpa_or_class_threshold',
      title: 'Gpa Or Class Threshold',
      type: 'string',
    }),
    defineField({
      name: 'decision_point_timing',
      title: 'Decision Point Timing',
      type: 'string',
    }),
  ],
})
