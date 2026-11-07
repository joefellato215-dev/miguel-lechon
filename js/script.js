/*
 * Miguel Lechon
 * Main JavaScript
 *
 * Vanilla JavaScript only.
 */

"use strict";

/* ==========================================================
   MOBILE NAVIGATION
========================================================== */

const menuButton = document.getElementById("menuButton");
const mobileMenu = document.getElementById("mobileMenu");

if (menuButton && mobileMenu) {
  menuButton.addEventListener("click", () => {
    const isOpen =
      menuButton.getAttribute("aria-expanded") === "true";

    menuButton.setAttribute(
      "aria-expanded",
      String(!isOpen)
    );

    mobileMenu.classList.toggle("hidden", isOpen);

    menuButton.setAttribute(
      "aria-label",
      isOpen
        ? "Open navigation menu"
        : "Close navigation menu"
    );
  });

  /*
   * Close the mobile menu after a navigation link is selected.
   */
  mobileMenu
    .querySelectorAll("a")
    .forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.add("hidden");

        menuButton.setAttribute(
          "aria-expanded",
          "false"
        );

        menuButton.setAttribute(
          "aria-label",
          "Open navigation menu"
        );
      });
    });
}


/* ==========================================================
   SCROLL REVEAL
========================================================== */

const revealElements =
  document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const revealObserver =
    new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }

          entry.target.classList.add("is-visible");

          observer.unobserve(entry.target);
        });
      },
      {
        threshold: 0.12
      }
    );

  revealElements.forEach((element) => {
    revealObserver.observe(element);
  });
} else {
  /*
   * Fallback for older browsers.
   */
  revealElements.forEach((element) => {
    element.classList.add("is-visible");
  });
}


/* ==========================================================
   ORDER FORM
========================================================== */

const orderForm =
  document.getElementById("orderForm");

const formStatus =
  document.getElementById("formStatus");

if (orderForm) {
  orderForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (orderForm.dataset.submitting === "true") {
      return;
    }

    const formData =
      new FormData(orderForm);

    const name =
      String(formData.get("name") || "").trim();

    const phone =
      String(formData.get("phone") || "").trim();

    const eventDate =
      String(formData.get("eventDate") || "").trim();

    const size =
      String(formData.get("size") || "").trim();

    const notes =
      String(formData.get("notes") || "").trim();

    const contactMethod =
      String(
        formData.get("contactMethod") ||
        "messenger"
      ).trim().toLowerCase();

    if (formStatus) {
      formStatus.textContent =
        "Saving your order inquiry...";

      formStatus.classList.remove("hidden");
    }

    orderForm.dataset.submitting = "true";

    const submitButton =
      orderForm.querySelector('button[type="submit"]');

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.dataset.originalText =
        submitButton.textContent;
      submitButton.textContent =
        "Saving...";
    }

    try {
      const response =
        await fetch("/api/orders", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify({
            name,
            phone,
            eventDate,
            size,
            notes,
            contactMethod
          })
        });

      const data =
        await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(
          data.error ||
          "Unable to save your order inquiry."
        );
      }

      const orderId =
        data.order && data.order.id
          ? data.order.id
          : null;

      const message = [
        "Hello Miguel Lechon! I'd like to inquire about an order.",
        "",
        orderId
          ? `Order Inquiry #: ${orderId}`
          : "",
        `Name: ${name}`,
        `Phone: ${phone}`,
        `Event Date: ${eventDate}`,
        `Preferred Order: ${size}`,
        `Notes: ${notes || "None"}`,
        "",
        "Please let me know the availability and total price. Thank you!"
      ]
        .filter(Boolean)
        .join("\n");

      const encodedMessage =
        encodeURIComponent(message);

      let destination = "";

      /*
       * Messenger:
       *
       * The business Messenger URL is still a placeholder.
       * The order is already saved in SQLite before this point.
       */
      if (contactMethod === "messenger") {
        destination = "https://www.facebook.com/share/1aHSZGJK2i/";
      }

      /*
       * Viber
       */
      if (contactMethod === "viber") {
        destination =
          `viber://chat?number=09771200663&text=${encodedMessage}`;
      }

      /*
       * SMS
       */
      if (contactMethod === "sms") {
        destination =
          `sms:09771200663?body=${encodedMessage}`;
      }

      /*
       * If the selected contact channel is not configured yet,
       * keep the customer on the page and confirm the saved order.
       */
      if (
        !destination ||
        destination.includes("https://www.facebook.com/share/1aHSZGJK2i/")
      ) {
        if (formStatus) {
          formStatus.textContent =
            orderId
              ? `Order inquiry #${orderId} saved successfully. We will contact you soon.`
              : "Order inquiry saved successfully. We will contact you soon.";
        }

        orderForm.reset();

        const messengerRadio =
          orderForm.querySelector(
            'input[name="contactMethod"][value="messenger"]'
          );

        if (messengerRadio) {
          messengerRadio.checked = true;
        }

        return;
      }

      if (formStatus) {
        formStatus.textContent =
          orderId
            ? `Order inquiry #${orderId} saved. Opening your selected messaging app...`
            : "Order saved. Opening your selected messaging app...";

        formStatus.classList.remove("hidden");
      }

      window.setTimeout(() => {
        window.location.href = destination;
      }, 150);

    } catch (error) {
      console.error(
        "Order submission failed:",
        error
      );

      if (formStatus) {
        formStatus.textContent =
          error.message ||
          "Unable to save your order inquiry. Please try again.";

        formStatus.classList.remove("hidden");
      }

    } finally {
      orderForm.dataset.submitting = "false";

      if (submitButton) {
        submitButton.disabled = false;

        submitButton.textContent =
          submitButton.dataset.originalText ||
          "Submit Order Inquiry";
      }
    }
  });
}


/* ==========================================================
   FOOTER YEAR
========================================================== */

const yearElement =
  document.getElementById("year");

if (yearElement) {
  yearElement.textContent =
    new Date().getFullYear();
}


/* ==========================================================
   PREVENT PAST DATES IN ORDER FORM
========================================================== */

const eventDateInput =
  document.getElementById("eventDate");

if (eventDateInput) {
  const today =
    new Date().toISOString().split("T")[0];

  eventDateInput.min = today;
}
