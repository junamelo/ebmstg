package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "sessions")
public class SessionUtilisateur {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "utilisateur_id", nullable = false)
    private Utilisateur utilisateur; // Utilisateur 1 -> 0..* Session

    @Column(nullable = false)
    private String refreshToken;

    private String ipAddress;
    private String userAgent;
    private LocalDateTime expireAt;
    private boolean estActive;
}
