// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.living_cost_source_basis) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'livingCostSourceBasis',
  title: 'Living Cost Source Basis',
  type: 'object',
  fields: [
    defineField({
      name: 'kind',
      title: 'Kind',
      type: 'string',
      options: { list: ["genuine_cost_of_living_estimate", "government_minimum_income_threshold", "not_published"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'administering_body',
      title: 'Administering Body',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
  ],
})
