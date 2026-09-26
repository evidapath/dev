// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.cost_profile) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'costProfile',
  title: 'Cost Profile',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'program_ref',
      title: 'Program',
      type: 'reference',
      weak: true,
      to: [{ type: 'program' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'academic_year',
      title: 'Academic Year',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'residency_category_ref',
      title: 'Residency Category',
      type: 'reference',
      weak: true,
      to: [{ type: 'applicantCategory' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'currency',
      title: 'Currency',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'tuition_annual',
      title: 'Tuition Annual',
      type: 'number',
    }),
    defineField({
      name: 'tuition_basis',
      title: 'Tuition Basis',
      type: 'string',
      options: { list: ["statutory", "institutional", "per-credit", "per-program", "other"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'mandatory_fees_annual',
      title: 'Mandatory Fees Annual',
      type: 'number',
    }),
    defineField({
      name: 'mandatory_fees_breakdown',
      title: 'Mandatory Fees Breakdown',
      type: 'array',
      of: [{ type: 'lineItem' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'estimated_living_costs_annual',
      title: 'Estimated Living Costs Annual',
      type: 'number',
    }),
    defineField({
      name: 'living_cost_source_basis',
      title: 'Living Cost Source Basis',
      type: 'livingCostSourceBasis',
    }),
    defineField({
      name: 'other_material_costs',
      title: 'Other Material Costs',
      type: 'array',
      of: [{ type: 'lineItem' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'duration_years',
      title: 'Duration Years',
      type: 'number',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'last_checked',
      title: 'Last Checked',
      type: 'string', // unresolved $ref: iso_date
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'verification_status',
      title: 'Verification Status',
      type: 'string',
      options: { list: ["VERIFIED", "VERIFIED_ABSENT", "SUPPORTED", "ESTIMATED", "UNKNOWN", "CONFLICT"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'record_status',
      title: 'Record Status',
      type: 'string',
      options: { list: ["RESEARCHED", "STRUCTURED", "VERIFIED", "HUMAN_REVIEW", "APPROVED", "PUBLISHED"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'extension_metadata',
      title: 'Extension Metadata',
      type: 'extensionMetadata',
    }),
    defineField({
      name: 'estimated_living_costs_monthly_range',
      title: 'Estimated Living Costs Monthly Range',
      type: 'monthlyRange',
    }),
    defineField({
      name: 'college_ref',
      title: 'College',
      type: 'reference',
      weak: true,
      to: [{ type: 'college' }],
    }),
    defineField({
      name: 'program_pathway_ref',
      title: 'Program Pathway',
      type: 'reference',
      weak: true,
      to: [{ type: 'programPathway' }],
    }),
  ],
  preview: {
    select: {"currency": "currency", "tuition": "tuition_annual", "year": "academic_year", "id": "id"},
    prepare: ({currency, tuition, year, id}) => ({ title: (tuition !== undefined && tuition !== null) ? [currency, tuition].filter(Boolean).join(' ') : id, subtitle: [year, id].filter(Boolean).join(' · ') }),
  },
})
