package com.adminstarter.keycloak.events;

import org.keycloak.Config;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventListenerProviderFactory;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;

public final class DisableAfterEmailVerifyEventListenerProviderFactory
    implements EventListenerProviderFactory {
  public static final String PROVIDER_ID = "disable-after-email-verify";

  @Override
  public EventListenerProvider create(KeycloakSession session) {
    return new DisableAfterEmailVerifyEventListenerProvider(session);
  }

  @Override
  public void init(Config.Scope config) {}

  @Override
  public void postInit(KeycloakSessionFactory factory) {}

  @Override
  public void close() {}

  @Override
  public String getId() {
    return PROVIDER_ID;
  }
}
