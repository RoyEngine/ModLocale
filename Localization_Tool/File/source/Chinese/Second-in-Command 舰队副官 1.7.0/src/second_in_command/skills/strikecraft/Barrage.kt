package second_in_command.skills.strikecraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.combat.WeaponAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Barrage : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有战机"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+100%% 导弹武器备弹量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-33%% 导弹武器伤害", 0f, Misc.getNegativeHighlightColor(), Misc.getNegativeHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun applyEffectsToFighterSpawnedByShip(data: SCData, fighter: ShipAPI?, ship: ShipAPI?, id: String?) {
        var stats = fighter!!.mutableStats

        stats.missileAmmoBonus.modifyPercent(id, 100f)
        stats.missileWeaponDamageMult.modifyMult(id, 0.666f)

        for (weapon in fighter.allWeapons) {
            if (weapon.type == WeaponAPI.WeaponType.MISSILE || weapon.type == WeaponAPI.WeaponType.COMPOSITE || weapon.type == WeaponAPI.WeaponType.SYNERGY)  {
                weapon.maxAmmo = fighter.mutableStats.missileAmmoBonus.computeEffective(weapon.spec.maxAmmo.toFloat()).toInt()
                weapon.resetAmmo()
            }
        }
    }

}