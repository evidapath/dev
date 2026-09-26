// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.test_requirement) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'testRequirement',
  title: 'Test Requirement',
  type: 'object',
  fields: [
    defineField({
      name: 'test_name',
      title: 'Test Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'min_score',
      title: 'Min Score',
      type: 'string', // source field is string|number|null -- see validation-rules.md
    }),
    defineField({
      name: 'required',
      title: 'Required',
      type: 'string',
      options: { list: ["required", "recommended"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
    }),
  ],
})
