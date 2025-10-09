<template>
	<div class="support">
		<div class="page-header">
			<h2>{{ $__('Support & Help') }}</h2>
			<p>{{ $__('Get help and support for your queries') }}</p>
		</div>

		<div class="support-container">
			<!-- Create New Support Ticket -->
			<div class="create-ticket-card">
				<h3>{{ $__('Create Support Ticket') }}</h3>
				<form @submit.prevent="createTicket" class="ticket-form">
					<div class="form-group">
						<label>{{ $__('Subject') }}</label>
						<input 
							v-model="newTicket.subject" 
							type="text" 
							:placeholder="$__('Enter ticket subject')"
							required
						>
					</div>
					
					<div class="form-group">
						<label>{{ $__('Category') }}</label>
						<select v-model="newTicket.category" required>
							<option value="">{{ $__('Select Category') }}</option>
							<option value="technical">{{ $__('Technical Issue') }}</option>
							<option value="vehicle">{{ $__('Vehicle Issue') }}</option>
							<option value="fuel">{{ $__('Fuel Related') }}</option>
							<option value="trip">{{ $__('Trip Related') }}</option>
							<option value="account">{{ $__('Account Issue') }}</option>
							<option value="other">{{ $__('Other') }}</option>
						</select>
					</div>
					
					<div class="form-group">
						<label>{{ $__('Priority') }}</label>
						<select v-model="newTicket.priority" required>
							<option value="low">{{ $__('Low') }}</option>
							<option value="medium">{{ $__('Medium') }}</option>
							<option value="high">{{ $__('High') }}</option>
							<option value="urgent">{{ $__('Urgent') }}</option>
						</select>
					</div>
					
					<div class="form-group">
						<label>{{ $__('Description') }}</label>
						<textarea 
							v-model="newTicket.description" 
							:placeholder="$__('Describe your issue in detail')"
							rows="5"
							required
						></textarea>
					</div>
					
					<div class="form-group">
						<label>{{ $__('Attachments') }}</label>
						<input 
							type="file" 
							@change="handleFileUpload"
							multiple
							accept="image/*,.pdf,.doc,.docx"
						>
						<small class="help-text">{{ $__('Supported formats: Images, PDF, Word documents') }}</small>
					</div>
					
					<button type="submit" class="submit-btn" :disabled="isSubmitting">
						<i class="fa fa-paper-plane"></i>
						{{ isSubmitting ? $__('Creating...') : $__('Create Ticket') }}
					</button>
				</form>
			</div>

			<!-- Current Support Tickets -->
			<div class="tickets-card">
				<div class="card-header">
					<h3>{{ $__('My Support Tickets') }}</h3>
					<div class="filters">
						<select v-model="ticketFilter" @change="loadTickets">
							<option value="all">{{ $__('All Tickets') }}</option>
							<option value="open">{{ $__('Open') }}</option>
							<option value="in_progress">{{ $__('In Progress') }}</option>
							<option value="resolved">{{ $__('Resolved') }}</option>
							<option value="closed">{{ $__('Closed') }}</option>
						</select>
					</div>
				</div>

				<div v-if="tickets.length === 0" class="empty-state">
					<i class="fa fa-ticket-alt"></i>
					<p>{{ $__('No support tickets found') }}</p>
				</div>

				<div v-else class="tickets-list">
					<div 
						v-for="ticket in tickets" 
						:key="ticket.name" 
						class="ticket-item"
						@click="viewTicket(ticket)"
					>
						<div class="ticket-header">
							<div class="ticket-info">
								<h4>{{ ticket.subject }}</h4>
								<p class="ticket-id">{{ $__('Ticket') }} #{{ ticket.name }}</p>
							</div>
							<div class="ticket-meta">
								<span :class="'priority-badge priority-' + ticket.priority">
									{{ $__(ticket.priority) }}
								</span>
								<span :class="'status-badge status-' + ticket.status">
									{{ $__(ticket.status) }}
								</span>
							</div>
						</div>
						
						<div class="ticket-details">
							<div class="ticket-category">
								<i class="fa fa-tag"></i>
								{{ $__(ticket.category) }}
							</div>
							<div class="ticket-date">
								<i class="fa fa-calendar"></i>
								{{ formatDate(ticket.creation) }}
							</div>
							<div v-if="ticket.assigned_to" class="ticket-assignee">
								<i class="fa fa-user"></i>
								{{ ticket.assigned_to }}
							</div>
						</div>
						
						<div class="ticket-description">
							{{ ticket.description.substring(0, 150) }}...
						</div>
					</div>
				</div>
			</div>

			<!-- Quick Contact Information -->
			<div class="quick-contact-card">
				<h3>{{ $__('Quick Contact') }}</h3>
				<div class="contact-options">
					<div class="contact-item">
						<div class="contact-icon">
							<i class="fa fa-phone"></i>
						</div>
						<div class="contact-info">
							<h4>{{ $__('Emergency Hotline') }}</h4>
							<p>{{ $__('24/7 Emergency Support') }}</p>
							<a href="tel:+966800123456" class="contact-link">+966 800 123 456</a>
						</div>
					</div>
					
					<div class="contact-item">
						<div class="contact-icon">
							<i class="fa fa-envelope"></i>
						</div>
						<div class="contact-info">
							<h4>{{ $__('Email Support') }}</h4>
							<p>{{ $__('General inquiries and support') }}</p>
							<a href="mailto:support@company.com" class="contact-link">support@company.com</a>
						</div>
					</div>
					
					<div class="contact-item">
						<div class="contact-icon">
							<i class="fa fa-comments"></i>
						</div>
						<div class="contact-info">
							<h4>{{ $__('Live Chat') }}</h4>
							<p>{{ $__('Chat with our support team') }}</p>
							<button @click="startLiveChat" class="contact-link btn">{{ $__('Start Chat') }}</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Frequently Asked Questions -->
			<div class="faq-card">
				<h3>{{ $__('Frequently Asked Questions') }}</h3>
				<div class="faq-list">
					<div 
						v-for="(faq, index) in faqs" 
						:key="index" 
						class="faq-item"
						:class="{ active: faq.isOpen }"
						@click="toggleFAQ(index)"
					>
						<div class="faq-question">
							<h4>{{ $__(faq.question) }}</h4>
							<i class="fa fa-chevron-down"></i>
						</div>
						<div class="faq-answer" v-show="faq.isOpen">
							<p>{{ $__(faq.answer) }}</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Ticket View Modal -->
		<div v-if="selectedTicket" class="ticket-modal" @click="closeTicketModal">
			<div class="modal-content" @click.stop>
				<div class="modal-header">
					<h3>{{ selectedTicket.subject }}</h3>
					<button @click="closeTicketModal" class="close-btn">
						<i class="fa fa-times"></i>
					</button>
				</div>
				
				<div class="modal-body">
					<div class="ticket-details-full">
						<div class="detail-row">
							<label>{{ $__('Ticket ID') }}:</label>
							<span>{{ selectedTicket.name }}</span>
						</div>
						<div class="detail-row">
							<label>{{ $__('Status') }}:</label>
							<span :class="'status-badge status-' + selectedTicket.status">
								{{ $__(selectedTicket.status) }}
							</span>
						</div>
						<div class="detail-row">
							<label>{{ $__('Priority') }}:</label>
							<span :class="'priority-badge priority-' + selectedTicket.priority">
								{{ $__(selectedTicket.priority) }}
							</span>
						</div>
						<div class="detail-row">
							<label>{{ $__('Category') }}:</label>
							<span>{{ $__(selectedTicket.category) }}</span>
						</div>
						<div class="detail-row">
							<label>{{ $__('Created') }}:</label>
							<span>{{ formatDate(selectedTicket.creation) }}</span>
						</div>
						<div v-if="selectedTicket.assigned_to" class="detail-row">
							<label>{{ $__('Assigned to') }}:</label>
							<span>{{ selectedTicket.assigned_to }}</span>
						</div>
					</div>
					
					<div class="ticket-description-full">
						<h4>{{ $__('Description') }}</h4>
						<p>{{ selectedTicket.description }}</p>
					</div>
					
					<!-- Ticket Comments -->
					<div class="ticket-comments">
						<h4>{{ $__('Comments') }}</h4>
						<div v-if="selectedTicket.comments && selectedTicket.comments.length > 0" class="comments-list">
							<div v-for="comment in selectedTicket.comments" :key="comment.name" class="comment-item">
								<div class="comment-header">
									<strong>{{ comment.comment_by }}</strong>
									<span class="comment-date">{{ formatDate(comment.creation) }}</span>
								</div>
								<div class="comment-content">{{ comment.content }}</div>
							</div>
						</div>
						<div v-else class="no-comments">
							<p>{{ $__('No comments yet') }}</p>
						</div>
						
						<!-- Add New Comment -->
						<div class="add-comment">
							<textarea 
								v-model="newComment" 
								:placeholder="$__('Add a comment...')"
								rows="3"
							></textarea>
							<button @click="addComment" class="add-comment-btn" :disabled="!newComment.trim()">
								<i class="fa fa-paper-plane"></i>
								{{ $__('Add Comment') }}
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Support',
	data() {
		return {
			newTicket: {
				subject: '',
				category: '',
				priority: 'medium',
				description: '',
				attachments: []
			},
			isSubmitting: false,
			tickets: [],
			ticketFilter: 'all',
			selectedTicket: null,
			newComment: '',
			faqs: [
				{
					question: 'How do I report a vehicle breakdown?',
					answer: 'You can report a vehicle breakdown by creating a support ticket with category "Vehicle Issue" or calling our emergency hotline at +966 800 123 456.',
					isOpen: false
				},
				{
					question: 'How do I update my fuel records?',
					answer: 'Go to the Fuel Management section in your dashboard to add, edit, or view your fuel records. Make sure to upload receipts for verification.',
					isOpen: false
				},
				{
					question: 'What should I do if I cannot start a trip?',
					answer: 'Check if the vehicle is properly assigned to you and if there are any pending maintenance issues. If the problem persists, contact support immediately.',
					isOpen: false
				},
				{
					question: 'How do I change my password?',
					answer: 'Contact your system administrator or HR department to reset your password. For security reasons, password changes must be done through proper channels.',
					isOpen: false
				},
				{
					question: 'Who do I contact for payroll issues?',
					answer: 'For payroll-related questions, please contact the HR department directly or create a support ticket with category "Account Issue".',
					isOpen: false
				}
			]
		}
	},
	mounted() {
		this.loadTickets()
	},
	methods: {
		async loadTickets() {
			try {
				const response = await frappe.call({
					method: 'logistay.api.support.get_driver_tickets',
					args: { status: this.ticketFilter === 'all' ? null : this.ticketFilter }
				})
				if (response.message) {
					this.tickets = response.message
				}
			} catch (error) {
				console.error('Error loading tickets:', error)
				// Test data
				this.tickets = [
					{
						name: 'TKT-001',
						subject: 'Vehicle AC not working',
						category: 'vehicle',
						priority: 'high',
						status: 'open',
						description: 'The air conditioning system in vehicle ABC-123 is not working properly. It only blows warm air.',
						creation: '2024-01-15 10:30:00',
						assigned_to: 'Support Team'
					},
					{
						name: 'TKT-002',
						subject: 'Unable to access fuel records',
						category: 'technical',
						priority: 'medium',
						status: 'in_progress',
						description: 'I cannot access my fuel records in the system. Getting an error message when trying to view the fuel page.',
						creation: '2024-01-14 14:20:00',
						assigned_to: 'IT Support'
					}
				]
			}
		},

		async createTicket() {
			if (!this.newTicket.subject || !this.newTicket.category || !this.newTicket.description) {
				frappe.show_alert({
					message: this.$__('Please fill all required fields'),
					indicator: 'red'
				})
				return
			}

			this.isSubmitting = true
			try {
				const response = await frappe.call({
					method: 'logistay.api.support.create_ticket',
					args: {
						subject: this.newTicket.subject,
						category: this.newTicket.category,
						priority: this.newTicket.priority,
						description: this.newTicket.description,
						attachments: this.newTicket.attachments
					}
				})

				if (response.message) {
					frappe.show_alert({
						message: this.$__('Support ticket created successfully'),
						indicator: 'green'
					})
					
					// Reset form
					this.newTicket = {
						subject: '',
						category: '',
						priority: 'medium',
						description: '',
						attachments: []
					}
					
					// Reload tickets
					this.loadTickets()
				}
			} catch (error) {
				console.error('Error creating ticket:', error)
				frappe.show_alert({
					message: this.$__('Error creating support ticket'),
					indicator: 'red'
				})
			} finally {
				this.isSubmitting = false
			}
		},

		handleFileUpload(event) {
			const files = Array.from(event.target.files)
			this.newTicket.attachments = files
		},

		viewTicket(ticket) {
			this.selectedTicket = { ...ticket }
			// Load ticket comments
			this.loadTicketComments(ticket.name)
		},

		async loadTicketComments(ticketName) {
			try {
				const response = await frappe.call({
					method: 'logistay.api.support.get_ticket_comments',
					args: { ticket: ticketName }
				})
				if (response.message) {
					this.selectedTicket.comments = response.message
				}
			} catch (error) {
				console.error('Error loading ticket comments:', error)
				this.selectedTicket.comments = []
			}
		},

		closeTicketModal() {
			this.selectedTicket = null
			this.newComment = ''
		},

		async addComment() {
			if (!this.newComment.trim()) return

			try {
				const response = await frappe.call({
					method: 'logistay.api.support.add_ticket_comment',
					args: {
						ticket: this.selectedTicket.name,
						comment: this.newComment
					}
				})

				if (response.message) {
					frappe.show_alert({
						message: this.$__('Comment added successfully'),
						indicator: 'green'
					})
					
					this.newComment = ''
					this.loadTicketComments(this.selectedTicket.name)
				}
			} catch (error) {
				console.error('Error adding comment:', error)
				frappe.show_alert({
					message: this.$__('Error adding comment'),
					indicator: 'red'
				})
			}
		},

		toggleFAQ(index) {
			this.faqs[index].isOpen = !this.faqs[index].isOpen
		},

		startLiveChat() {
			// Execute live chat
			frappe.show_alert({
				message: this.$__('Live chat feature will be available soon'),
				indicator: 'blue'
			})
		},

		formatDate(dateStr) {
			if (!dateStr) return ''
			return new Date(dateStr).toLocaleDateString('ar-SA', {
				year: 'numeric',
				month: 'short',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			})
		}
	}
}
</script>

<style scoped>
.support {
	max-width: 1200px;
	margin: 0 auto;
}

.page-header {
	margin-bottom: 2rem;
}

.page-header h2 {
	color: #2c3e50;
	margin: 0 0 0.5rem 0;
}

.page-header p {
	color: #6c757d;
	margin: 0;
}

.support-container {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 2rem;
}

.create-ticket-card,
.tickets-card,
.quick-contact-card,
.faq-card {
	background: white;
	border-radius: 12px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	padding: 2rem;
}

.create-ticket-card {
	grid-column: 1 / -1;
}

.create-ticket-card h3,
.tickets-card h3,
.quick-contact-card h3,
.faq-card h3 {
	color: #2c3e50;
	margin-bottom: 1.5rem;
}

.ticket-form {
	display: grid;
	gap: 1rem;
}

.form-group {
	display: flex;
	flex-direction: column;
}

.form-group label {
	font-weight: 600;
	color: #2c3e50;
	margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
	padding: 0.75rem;
	border: 2px solid #e9ecef;
	border-radius: 8px;
	font-size: 0.95rem;
	transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
	outline: none;
	border-color: #667eea;
}

.help-text {
	color: #6c757d;
	font-size: 0.8rem;
	margin-top: 0.25rem;
}

.submit-btn {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	border: none;
	padding: 1rem 2rem;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.3s ease;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.submit-btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 1.5rem;
}

.filters select {
	padding: 0.5rem;
	border: 2px solid #e9ecef;
	border-radius: 6px;
}

.empty-state {
	text-align: center;
	padding: 3rem;
	color: #6c757d;
}

.empty-state i {
	font-size: 3rem;
	margin-bottom: 1rem;
	display: block;
}

.tickets-list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.ticket-item {
	border: 2px solid #e9ecef;
	border-radius: 8px;
	padding: 1.5rem;
	cursor: pointer;
	transition: all 0.3s ease;
}

.ticket-item:hover {
	border-color: #667eea;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ticket-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 1rem;
}

.ticket-info h4 {
	color: #2c3e50;
	margin: 0 0 0.25rem 0;
}

.ticket-id {
	color: #6c757d;
	font-size: 0.85rem;
	margin: 0;
}

.ticket-meta {
	display: flex;
	gap: 0.5rem;
}

.priority-badge,
.status-badge {
	padding: 0.25rem 0.75rem;
	border-radius: 20px;
	font-size: 0.75rem;
	font-weight: 600;
}

.priority-low { background: #d4edda; color: #155724; }
.priority-medium { background: #fff3cd; color: #856404; }
.priority-high { background: #f8d7da; color: #721c24; }
.priority-urgent { background: #721c24; color: white; }

.status-open { background: #cce5ff; color: #004085; }
.status-in_progress { background: #fff3cd; color: #856404; }
.status-resolved { background: #d4edda; color: #155724; }
.status-closed { background: #e2e3e5; color: #383d41; }

.ticket-details {
	display: flex;
	gap: 1rem;
	margin-bottom: 1rem;
	font-size: 0.85rem;
	color: #6c757d;
}

.ticket-details > div {
	display: flex;
	align-items: center;
	gap: 0.25rem;
}

.ticket-description {
	color: #495057;
	font-size: 0.9rem;
	line-height: 1.5;
}

.contact-options {
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}

.contact-item {
	display: flex;
	align-items: center;
	gap: 1rem;
	padding: 1rem;
	background: #f8f9fa;
	border-radius: 8px;
}

.contact-icon {
	width: 50px;
	height: 50px;
	border-radius: 50%;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 1.2rem;
}

.contact-info h4 {
	color: #2c3e50;
	margin: 0 0 0.25rem 0;
}

.contact-info p {
	color: #6c757d;
	margin: 0 0 0.5rem 0;
	font-size: 0.85rem;
}

.contact-link {
	color: #667eea;
	text-decoration: none;
	font-weight: 600;
}

.contact-link.btn {
	background: #667eea;
	color: white;
	padding: 0.5rem 1rem;
	border: none;
	border-radius: 6px;
	cursor: pointer;
}

.faq-list {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
}

.faq-item {
	border: 2px solid #e9ecef;
	border-radius: 8px;
	overflow: hidden;
	cursor: pointer;
	transition: border-color 0.3s ease;
}

.faq-item:hover,
.faq-item.active {
	border-color: #667eea;
}

.faq-question {
	padding: 1rem;
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #f8f9fa;
}

.faq-question h4 {
	color: #2c3e50;
	margin: 0;
	font-size: 0.95rem;
}

.faq-question i {
	color: #6c757d;
	transition: transform 0.3s ease;
}

.faq-item.active .faq-question i {
	transform: rotate(180deg);
}

.faq-answer {
	padding: 1rem;
	background: white;
}

.faq-answer p {
	color: #495057;
	margin: 0;
	line-height: 1.6;
}

/* Ticket View Modal */
.ticket-modal {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	background: white;
	border-radius: 12px;
	width: 90%;
	max-width: 800px;
	max-height: 90vh;
	overflow-y: auto;
}

.modal-header {
	padding: 2rem;
	border-bottom: 2px solid #e9ecef;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.modal-header h3 {
	color: #2c3e50;
	margin: 0;
}

.close-btn {
	background: none;
	border: none;
	font-size: 1.5rem;
	color: #6c757d;
	cursor: pointer;
	padding: 0.5rem;
	border-radius: 50%;
	transition: background-color 0.3s ease;
}

.close-btn:hover {
	background: #f8f9fa;
}

.modal-body {
	padding: 2rem;
}

.ticket-details-full {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 1rem;
	margin-bottom: 2rem;
}

.detail-row {
	display: flex;
	flex-direction: column;
	gap: 0.25rem;
}

.detail-row label {
	font-weight: 600;
	color: #6c757d;
	font-size: 0.85rem;
}

.ticket-description-full {
	margin-bottom: 2rem;
}

.ticket-description-full h4 {
	color: #2c3e50;
	margin-bottom: 1rem;
}

.ticket-comments {
	border-top: 2px solid #e9ecef;
	padding-top: 2rem;
}

.ticket-comments h4 {
	color: #2c3e50;
	margin-bottom: 1rem;
}

.comments-list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
	margin-bottom: 2rem;
}

.comment-item {
	background: #f8f9fa;
	padding: 1rem;
	border-radius: 8px;
	border-left: 4px solid #667eea;
}

.comment-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 0.5rem;
}

.comment-date {
	color: #6c757d;
	font-size: 0.8rem;
}

.comment-content {
	color: #495057;
	line-height: 1.5;
}

.no-comments {
	text-align: center;
	padding: 2rem;
	color: #6c757d;
}

.add-comment {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.add-comment textarea {
	padding: 0.75rem;
	border: 2px solid #e9ecef;
	border-radius: 8px;
	resize: vertical;
}

.add-comment-btn {
	background: #28a745;
	color: white;
	border: none;
	padding: 0.75rem 1.5rem;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	display: flex;
	align-items: center;
	gap: 0.5rem;
	align-self: flex-start;
}

.add-comment-btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

@media (max-width: 768px) {
	.support-container {
		grid-template-columns: 1fr;
	}
	
	.ticket-header {
		flex-direction: column;
		gap: 1rem;
	}
	
	.ticket-meta {
		align-self: flex-start;
	}
	
	.ticket-details {
		flex-direction: column;
		gap: 0.5rem;
	}
	
	.contact-item {
		flex-direction: column;
		text-align: center;
	}
	
	.modal-content {
		width: 95%;
		margin: 1rem;
	}
	
	.ticket-details-full {
		grid-template-columns: 1fr;
	}
}
</style>