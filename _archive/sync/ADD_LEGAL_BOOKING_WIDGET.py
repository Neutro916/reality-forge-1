"""
ADD BOOKING WIDGET TO LEGAL ARSENAL PAGE
Adds interactive consultation booking system
"""

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Arsenal - Builder Protection & Legal Empowerment | Consciousness Revolution</title>
    <meta name="description" content="Legal protection for builders. Automated demand letters, criminal complaint tools, attorney network, and legal AI analysis. Defend against corporate extortion.">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --legal-dark: #1a1a1a;
            --legal-gold: #d4af37;
            --legal-white: #ffffff;
            --legal-gray: #333333;
            --legal-accent: #8b0000;
        }
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background: linear-gradient(135deg, var(--legal-dark) 0%, var(--legal-gray) 100%);
            color: var(--legal-white);
            line-height: 1.6;
        }
        .header {
            background: rgba(26, 26, 26, 0.95);
            border-bottom: 3px solid var(--legal-gold);
            padding: 2rem;
            text-align: center;
        }
        .header h1 {
            font-size: 3em;
            color: var(--legal-gold);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 0.5rem;
        }
        .header p {
            font-size: 1.3em;
            color: var(--legal-white);
            font-style: italic;
        }
        .hero {
            padding: 4rem 2rem;
            text-align: center;
            background: linear-gradient(to bottom, rgba(212, 175, 55, 0.1), transparent);
        }
        .hero h2 {
            font-size: 2.5em;
            color: var(--legal-gold);
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1.2em;
            max-width: 800px;
            margin: 0 auto 2rem;
        }
        .cta-button {
            display: inline-block;
            background: var(--legal-gold);
            color: var(--legal-dark);
            padding: 1rem 3rem;
            font-size: 1.2em;
            font-weight: bold;
            text-decoration: none;
            border-radius: 5px;
            transition: all 0.3s;
            border: 2px solid var(--legal-gold);
            cursor: pointer;
        }
        .cta-button:hover {
            background: transparent;
            color: var(--legal-gold);
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
        }
        .service-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 4rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .service-card {
            background: rgba(51, 51, 51, 0.8);
            padding: 2rem;
            border-radius: 10px;
            border: 2px solid var(--legal-gold);
            transition: all 0.3s;
        }
        .service-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        }
        .service-card h3 {
            color: var(--legal-gold);
            font-size: 1.8em;
            margin-bottom: 1rem;
        }
        .service-card .price {
            font-size: 2em;
            color: var(--legal-gold);
            font-weight: bold;
            margin: 1rem 0;
        }
        .footer {
            background: var(--legal-dark);
            padding: 3rem 2rem;
            text-align: center;
            border-top: 3px solid var(--legal-gold);
        }

        /* Booking Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            overflow-y: auto;
            padding: 2rem;
        }
        .modal.active {
            display: block;
        }
        .modal-content {
            background: var(--legal-gray);
            padding: 3rem;
            border-radius: 15px;
            border: 3px solid var(--legal-gold);
            max-width: 900px;
            margin: 2rem auto;
            position: relative;
        }
        .close-modal {
            position: absolute;
            top: 1rem;
            right: 1.5rem;
            font-size: 2.5em;
            color: var(--legal-gold);
            cursor: pointer;
            background: none;
            border: none;
            line-height: 1;
        }
        .close-modal:hover {
            color: var(--legal-white);
        }
        .modal h2 {
            color: var(--legal-gold);
            font-size: 2.2em;
            margin-bottom: 1rem;
        }
        .modal-step {
            display: none;
        }
        .modal-step.active {
            display: block;
        }
        .time-slots {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .time-slot { background: rgba(212,175,55,0.1); border: 2px solid var(--legal-gold); padding: 1.2rem; text-align: center; cursor: pointer; border-radius: 8px; transition: all 0.3s; }
        .time-slot:hover { background: rgba(212,175,55,0.3); transform: scale(1.05); }
        .time-slot.selected { background: var(--legal-gold); color: var(--legal-dark); font-weight: bold; }
        .time-slot .date { font-weight: bold; font-size: 1.1em; }
        .time-slot .time { margin-top: 0.5rem; font-size: 0.95em; }
        .form-group { margin: 1.5rem 0; }
        .form-group label { display: block; color: var(--legal-gold); margin-bottom: 0.5rem; font-weight: bold; }
        .form-group input, .form-group textarea { width: 100%; padding: 1rem; background: rgba(26,26,26,0.8); border: 2px solid var(--legal-gold); color: var(--legal-white); font-size: 1em; border-radius: 5px; font-family: inherit; }
        .form-group textarea { min-height: 120px; resize: vertical; }
        .loading { text-align: center; color: var(--legal-gold); font-size: 1.3em; padding: 3rem; }
        .booking-summary { background: rgba(212,175,55,0.1); padding: 1.5rem; border-radius: 8px; border: 2px solid var(--legal-gold); margin: 1.5rem 0; }
        .booking-summary p { margin: 0.5rem 0; }
        .booking-summary strong { color: var(--legal-gold); }
        .button-group { display: flex; gap: 1rem; margin-top: 2rem; }
        .button-group button { flex: 1; }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚖️ LEGAL ARSENAL ⚖️</h1>
        <p>"The Sword and Shield of the Conscious Builder"</p>
    </div>

    <div class="hero">
        <h2>Builders vs. Destroyers: Legal Warfare Edition</h2>
        <p>
            You're a builder creating value. They're destroyers extracting it through legal extortion.
            Corporate entities weaponize law to crush individuals. We give you the same weapons—automated,
            affordable, and devastatingly effective.
        </p>
        <a href="#services" class="cta-button">DEPLOY LEGAL ARSENAL NOW</a>
    </div>

    <div id="services" class="service-grid">
        <div class="service-card">
            <h3>📄 Automated Demand Letters</h3>
            <div class="price">$49</div>
            <p>Professional, legally-sound demand letters generated in minutes. U-Haul extortion? Corporate breach? Generate your demand letter now.</p>
            <button class="cta-button" onclick="openDemandLetterModal()">Generate Demand Letter</button>
        </div>

        <div class="service-card">
            <h3>⚖️ Legal Consultation</h3>
            <div class="price">$99</div>
            <p>30-minute strategic session with consciousness-elevated legal analysis. Book a time slot now.</p>
            <button class="cta-button" onclick="openBookingModal()">Book Consultation</button>
        </div>

        <div class="service-card">
            <h3>🔨 Criminal Complaint Generator</h3>
            <div class="price">$199</div>
            <p>Automated criminal complaint preparation for serious violations. Extortion, fraud, conversion.</p>
            <button class="cta-button" onclick="openComplaintModal()">File Criminal Complaint</button>
        </div>
    </div>

    <!-- Consultation Booking Modal -->
    <div id="bookingModal" class="modal">
        <div class="modal-content">
            <button class="close-modal" onclick="closeModal('bookingModal')">&times;</button>

            <!-- Step 1: Select Time -->
            <div id="step1" class="modal-step active">
                <h2>⚖️ Book Legal Consultation</h2>
                <p style="margin-bottom: 1.5rem;">Select an available 30-minute time slot. All times shown in Mountain Time (MT).</p>
                <div class="loading" id="loadingSlots">Loading available time slots...</div>
                <div class="time-slots" id="timeSlots" style="display: none;"></div>
                <button class="cta-button" onclick="nextStep()" id="selectTimeBtn" style="display: none; margin-top: 1.5rem;">Continue to Details →</button>
            </div>

            <!-- Step 2: Enter Details -->
            <div id="step2" class="modal-step">
                <h2>Consultation Details</h2>
                <div class="booking-summary" id="selectedSlotSummary"></div>
                <form id="bookingForm">
                    <div class="form-group">
                        <label for="clientName">Full Name *</label>
                        <input type="text" id="clientName" required>
                    </div>
                    <div class="form-group">
                        <label for="clientEmail">Email Address *</label>
                        <input type="email" id="clientEmail" required>
                    </div>
                    <div class="form-group">
                        <label for="clientPhone">Phone Number *</label>
                        <input type="tel" id="clientPhone" required>
                    </div>
                    <div class="form-group">
                        <label for="legalIssue">Brief Description of Legal Issue *</label>
                        <textarea id="legalIssue" required placeholder="Describe your situation in a few sentences..."></textarea>
                    </div>
                </form>
                <div class="button-group">
                    <button class="cta-button" onclick="prevStep()" style="background: transparent;">← Back</button>
                    <button class="cta-button" onclick="submitBooking()">Confirm & Pay $99 →</button>
                </div>
            </div>

            <!-- Step 3: Confirmation -->
            <div id="step3" class="modal-step">
                <h2>✅ Booking Confirmed!</h2>
                <div class="booking-summary" id="confirmationDetails"></div>
                <p style="margin: 2rem 0; font-size: 1.1em;">
                    You will receive a confirmation email with:
                    <br>• Meeting link (Zoom/Google Meet)
                    <br>• Preparation checklist
                    <br>• Direct contact information
                </p>
                <button class="cta-button" onclick="closeModal('bookingModal')">Done</button>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Legal Arsenal - Domain 9 of the Consciousness Revolution</p>
        <p>Deployed: November 6, 2025 | Week 1, Day 3 of Recursive Boot Protocol</p>
        <p>⚖️ Justice Through Pattern Recognition | Builders Protected | Destroyers Deterred</p>
    </div>

    <script src="UNIVERSAL_ANALYTICS_TRACKER.js"></script>
    <script>
        let selectedSlot = null;
        let availableSlots = [];

        // Open consultation booking modal
        async function openBookingModal() {
            document.getElementById('bookingModal').classList.add('active');
            document.getElementById('step1').classList.add('active');
            await loadTimeSlots();
        }

        // Close modal
        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
            resetBookingModal();
        }

        // Reset booking modal to initial state
        function resetBookingModal() {
            selectedSlot = null;
            document.getElementById('step1').classList.add('active');
            document.getElementById('step2').classList.remove('active');
            document.getElementById('step3').classList.remove('active');
            document.getElementById('bookingForm').reset();
        }

        // Load available time slots from API
        async function loadTimeSlots() {
            try {
                const response = await fetch('/api/consultation-booking');
                const data = await response.json();

                if (data.success && data.slots) {
                    availableSlots = data.slots;
                    displayTimeSlots(data.slots);
                } else {
                    throw new Error('No slots available');
                }
            } catch (error) {
                document.getElementById('loadingSlots').innerHTML =
                    '❌ Unable to load time slots. Please try again or contact support.';
                console.error('Error loading slots:', error);
            }
        }

        // Display time slots
        function displayTimeSlots(slots) {
            const container = document.getElementById('timeSlots');
            document.getElementById('loadingSlots').style.display = 'none';
            container.style.display = 'grid';
            container.innerHTML = '';

            slots.forEach((slot, index) => {
                const slotDiv = document.createElement('div');
                slotDiv.className = 'time-slot';
                slotDiv.onclick = () => selectSlot(index);
                slotDiv.innerHTML = `
                    <div class="date">${slot.date}</div>
                    <div class="time">${slot.time}</div>
                `;
                container.appendChild(slotDiv);
            });
        }

        // Select a time slot
        function selectSlot(index) {
            selectedSlot = availableSlots[index];

            // Update UI
            document.querySelectorAll('.time-slot').forEach((slot, i) => {
                if (i === index) {
                    slot.classList.add('selected');
                } else {
                    slot.classList.remove('selected');
                }
            });

            document.getElementById('selectTimeBtn').style.display = 'block';
        }

        // Next step
        function nextStep() {
            if (!selectedSlot) {
                alert('Please select a time slot');
                return;
            }

            document.getElementById('step1').classList.remove('active');
            document.getElementById('step2').classList.add('active');

            document.getElementById('selectedSlotSummary').innerHTML = `
                <p><strong>Selected Time:</strong> ${selectedSlot.date} at ${selectedSlot.time}</p>
                <p><strong>Duration:</strong> 30 minutes</p>
                <p><strong>Price:</strong> $99</p>
            `;
        }

        // Previous step
        function prevStep() {
            document.getElementById('step2').classList.remove('active');
            document.getElementById('step1').classList.add('active');
        }

        // Submit booking
        async function submitBooking() {
            const form = document.getElementById('bookingForm');
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const bookingData = {
                slot_datetime: selectedSlot.datetime,
                client_name: document.getElementById('clientName').value,
                client_email: document.getElementById('clientEmail').value,
                client_phone: document.getElementById('clientPhone').value,
                legal_issue: document.getElementById('legalIssue').value
            };

            try {
                const response = await fetch('/api/consultation-booking', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bookingData)
                });

                const result = await response.json();

                if (result.success) {
                    showConfirmation(result);
                } else {
                    alert('Booking failed: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Booking error: ' + error.message);
                console.error('Booking error:', error);
            }
        }

        // Show confirmation
        function showConfirmation(result) {
            document.getElementById('step2').classList.remove('active');
            document.getElementById('step3').classList.add('active');

            document.getElementById('confirmationDetails').innerHTML = `
                <p><strong>Booking ID:</strong> ${result.booking_id}</p>
                <p><strong>Date & Time:</strong> ${selectedSlot.date} at ${selectedSlot.time}</p>
                <p><strong>Client:</strong> ${document.getElementById('clientName').value}</p>
                <p><strong>Email:</strong> ${document.getElementById('clientEmail').value}</p>
                <p><strong>Amount Paid:</strong> $99</p>
            `;
        }

        // Placeholder functions for other services
        function openDemandLetterModal() {
            alert('Demand Letter Generator - Coming in next deployment. Use U-Haul demand letter template for now.');
        }

        function openComplaintModal() {
            alert('Criminal Complaint Generator - Coming in next deployment.');
        }
    </script>
</body>
</html>
"""

from pathlib import Path

# Write to file
output_path = Path.home() / "100X_DEPLOYMENT" / "domain-legal-arsenal.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'✅ Legal Arsenal booking widget written to: {output_path}')
