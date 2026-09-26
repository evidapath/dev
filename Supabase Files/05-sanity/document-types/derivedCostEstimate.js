// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.derived_cost_estimate) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'derivedCostEstimate',
  title: 'Derived Cost Estimate',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'cost_profile_ref',
      title: 'Cost Profile',
      type: 'reference',
      to: [{ type: 'costProfile' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'field_name',
      title: 'Field Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'value',
      title: 'Value',
      type: 'number',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'inputs',
      title: 'Inputs',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'formula_method',
      title: 'Formula Method',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'assumptions',
      title: 'Assumptions',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'calculation_version',
      title: 'Calculation Version',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'calculated_at',
      title: 'Calculated At',
      type: 'string', // unresolved $ref: iso_datetime
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {"a": "field_name", "b": "value", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [(b !== undefined && b !== null) ? String(b) : null, id].filter(Boolean).join(' · ') }),
  },
})
