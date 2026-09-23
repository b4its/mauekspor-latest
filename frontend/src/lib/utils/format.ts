import type { ComplianceTask, DocumentItem, RiskLevel, TaskStatus } from '$lib/data/trade';

export const currency = new Intl.NumberFormat('en-US', {
	style: 'currency',
	currency: 'USD',
	maximumFractionDigits: 0
});

export function statusTone(status: TaskStatus | RiskLevel | DocumentItem['status'] | string) {
	if (['Verified', 'Ready', 'Approved', 'Passed', 'Done', 'Delivered', 'Low', 'Enriched', 'Qualified', 'Active', 'Settled', 'Deposit Paid', 'Info', 'Read', 'Connected', 'Resolved', 'Complete', 'Published', 'Matched'].includes(status)) return 'green';
	if (['In Review', 'Evidence Uploaded', 'Needs Review', 'Current', 'Loaded', 'Customs Submitted', 'In Transit', 'Medium', 'Needs HS Review', 'Needs Evidence', 'Due Soon', 'Pending', 'Open', 'In Progress', 'Warning', 'Scheduled', 'Invited', 'Unread', 'Available', 'Needs Auth', 'Waiting Reply', 'Missing Metadata', 'Trial', 'Expiring Soon', 'Draft', 'New', 'Quoted'].includes(status)) return 'orange';
	if (['Blocked', 'Missing', 'Failed', 'Exception', 'High', 'Critical', 'At Risk', 'Overdue', 'Suspended', 'Error', 'Escalated', 'Past Due', 'Cancelled', 'Revoked'].includes(status)) return 'red';
	return 'blue';
}

export function taskSummary(tasks: ComplianceTask[]) {
	return {
		verified: tasks.filter((task) => task.status === 'Verified').length,
		blocked: tasks.filter((task) => task.status === 'Blocked').length,
		pending: tasks.filter((task) => task.status !== 'Verified').length
	};
}
