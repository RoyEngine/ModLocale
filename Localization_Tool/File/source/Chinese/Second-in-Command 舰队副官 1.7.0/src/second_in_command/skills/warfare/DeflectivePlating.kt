package second_in_command.skills.warfare

import com.fs.starfarer.api.combat.*
import com.fs.starfarer.api.combat.listeners.AdvanceableListener
import com.fs.starfarer.api.combat.listeners.DamageTakenModifier
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import org.lwjgl.util.vector.Vector2f
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class DeflectivePlating : SCBaseSkillPlugin() {


    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("船体结构受到单次超过 500 点的损伤时，使超出 500 点的损害削减 50%%，每艘舰船每 3 秒最多触发一次", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {



    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

        if (!ship!!.hasListenerOfClass(DeflectivePlatingListener::class.java)) {
            ship.addListener(DeflectivePlatingListener(ship))
        }

    }

    override fun onActivation(data: SCData) {

    }

    override fun onDeactivation(data: SCData) {

    }

}

class DeflectivePlatingListener(var ship: ShipAPI) : DamageTakenModifier, AdvanceableListener {

    var damageThreshold = 500f
    var damageReduction = 50f
    var secondsPerProc = 3f

    var sinceProc = secondsPerProc + 1f

    override fun advance(amount: Float) {
        sinceProc += amount
    }

    override fun modifyDamageTaken(param: Any?, target: CombatEntityAPI?, damage: DamageAPI?, point: Vector2f?, shieldHit: Boolean): String? {

        if (!shieldHit && sinceProc > secondsPerProc) {
            val mult = 1f - damageReduction / 100f
            ship!!.setNextHitHullDamageThresholdMult(damageThreshold, mult)
            sinceProc = 0f
        }

        return null
    }

}