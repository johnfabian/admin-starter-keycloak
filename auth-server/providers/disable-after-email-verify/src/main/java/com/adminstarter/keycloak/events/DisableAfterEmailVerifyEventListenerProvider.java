package com.adminstarter.keycloak.events;

import org.jboss.logging.Logger;
import org.keycloak.events.Event;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventType;
import org.keycloak.events.admin.AdminEvent;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

final class DisableAfterEmailVerifyEventListenerProvider implements EventListenerProvider {
  private static final Logger LOGGER =
      Logger.getLogger(DisableAfterEmailVerifyEventListenerProvider.class);

  static final String SELF_REGISTERED_ATTRIBUTE = "self_registered";
  static final String AWAITING_ADMIN_APPROVAL_ATTRIBUTE = "awaiting_admin_approval";
  static final String ENABLED_ATTRIBUTE_VALUE = "true";

  private final KeycloakSession session;

  DisableAfterEmailVerifyEventListenerProvider(KeycloakSession session) {
    this.session = session;
  }

  @Override
  public void onEvent(Event event) {
    if (event.getUserId() == null) {
      return;
    }

    if (event.getType() == EventType.REGISTER) {
      markSelfRegisteredUser(event);
      return;
    }

    if (event.getType() == EventType.VERIFY_EMAIL) {
      disableSelfRegisteredUserAfterEmailVerification(event);
    }
  }

  @Override
  public void onEvent(AdminEvent event, boolean includeRepresentation) {}

  @Override
  public void close() {}

  private void markSelfRegisteredUser(Event event) {
    RealmModel realm = getRealm(event);
    UserModel user = getUser(event, realm);

    if (user == null) {
      return;
    }

    user.setSingleAttribute(SELF_REGISTERED_ATTRIBUTE, ENABLED_ATTRIBUTE_VALUE);
    LOGGER.infof(
        "Marked self-registered user %s in realm %s for post-verification approval.",
        event.getUserId(), event.getRealmId());
  }

  private void disableSelfRegisteredUserAfterEmailVerification(Event event) {
    RealmModel realm = getRealm(event);
    UserModel user = getUser(event, realm);

    if (user == null || !hasEnabledAttribute(user, SELF_REGISTERED_ATTRIBUTE)) {
      return;
    }

    user.removeAttribute(SELF_REGISTERED_ATTRIBUTE);
    user.setSingleAttribute(AWAITING_ADMIN_APPROVAL_ATTRIBUTE, ENABLED_ATTRIBUTE_VALUE);

    if (!user.isEnabled()) {
      return;
    }

    user.setEnabled(false);
    session.sessions().removeUserSessions(realm, user);
    LOGGER.infof(
        "Disabled verified self-registered user %s in realm %s pending admin approval.",
        event.getUserId(), event.getRealmId());
  }

  private RealmModel getRealm(Event event) {
    RealmModel realm = session.realms().getRealm(event.getRealmId());

    if (realm == null) {
      LOGGER.warnf("Could not resolve realm %s for event %s.", event.getRealmId(), event.getType());
    }

    return realm;
  }

  private UserModel getUser(Event event, RealmModel realm) {
    if (realm == null) {
      return null;
    }

    UserModel user = session.users().getUserById(realm, event.getUserId());

    if (user == null) {
      LOGGER.warnf("Could not resolve user %s for event %s.", event.getUserId(), event.getType());
    }

    return user;
  }

  private boolean hasEnabledAttribute(UserModel user, String attribute) {
    return user.getAttributeStream(attribute).anyMatch(ENABLED_ATTRIBUTE_VALUE::equalsIgnoreCase);
  }
}
