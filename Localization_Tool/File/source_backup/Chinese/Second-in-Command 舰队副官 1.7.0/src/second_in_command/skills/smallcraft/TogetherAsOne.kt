package second_in_command.skills.smallcraft

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.combat.listeners.AdvanceableListener
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.IntervalUtil
import com.fs.starfarer.api.util.Misc
import org.lazywizard.lazylib.MathUtils
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class TogetherAsOne : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有护卫舰和驱逐舰"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {
        tooltip.addPara("护卫舰和驱逐舰靠近其他友军护卫舰和驱逐舰时，获得多种增益效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 本效果生效半径约为 1200",0f, Misc.getTextColor(), Misc.getHighlightColor(), "1200")
        tooltip.addPara("   - 附近存在 6 艘友舰时达到最大效果",0f, Misc.getTextColor(), Misc.getHighlightColor(), "6")
	tooltip.addPara("   - 每存在 1 艘友舰 +3%% 最高航速}、{幅能耗散}、以及{造成的伤害",0f, Misc.getTextColor(), Misc.getHighlightColor(), "+3%", "最高航速", "幅能耗散", "造成的伤害")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {
        if (!ship!!.hasListenerOfClass(TogetherAsOneScript::class.java) && (ship.hullSize == ShipAPI.HullSize.FRIGATE || ship.hullSize == ShipAPI.HullSize.DESTROYER)) {
            ship.addListener(TogetherAsOneScript(ship))
        }
    }

}

class TogetherAsOneScript(var ship: ShipAPI) : AdvanceableListener {

    var interval = IntervalUtil(0.2f, 0.2f)
    var recentCount = 0

    override fun advance(amount: Float) {

        if (ship == Global.getCombatEngine().playerShip && recentCount > 0) {

            var addedS = ""
            if (recentCount >= 2) {
                addedS = ""
            }

            Global.getCombatEngine().maintainStatusForPlayerShip("sc_together_as_one", "graphics/icons/hullsys/targeting_feed.png",
                "万众一心", "附近存在 $recentCount 艘友军舰船", false)
        }

        interval.advance(amount)
        if (!interval.intervalElapsed()) return

        var count = 0

        var iterator = Global.getCombatEngine().shipGrid.getCheckIterator(ship.location, 2000f, 2000f)
        for (entry in iterator) {
            var ally = entry as ShipAPI

            if (ally == ship) continue
            if (!ally.isAlive) continue
            if (ship.owner != ally.owner) continue
            if (ship.parentStation != null) continue

            if (!ally.isFrigate && !ally.isDestroyer) continue
            if (MathUtils.getDistance(ally, ship) >= 1200) continue

            count += 1
        }


        count = MathUtils.clamp(count, 0, 6)
        //var mod = 0.03f * count
        var mod = 3f * count

        /*ship.mutableStats.maxSpeed.modifyMult("sc_together_as_one", 1f + mod)
        ship.mutableStats.acceleration.modifyMult("sc_together_as_one", 1f + mod)
        ship.mutableStats.deceleration.modifyMult("sc_together_as_one", 1f + mod)

        ship.mutableStats.fluxDissipation.modifyMult("sc_together_as_one", 1f + mod)

        ship.mutableStats.ballisticWeaponDamageMult.modifyMult("sc_together_as_one", 1f + mod)
        ship.mutableStats.energyWeaponDamageMult.modifyMult("sc_together_as_one", 1f + mod)
        ship.mutableStats.missileWeaponDamageMult.modifyMult("sc_together_as_one", 1f + mod)*/

        ship.mutableStats.maxSpeed.modifyPercent("sc_together_as_one", mod)
        ship.mutableStats.acceleration.modifyPercent("sc_together_as_one", mod)
        ship.mutableStats.deceleration.modifyPercent("sc_together_as_one", mod)

        ship.mutableStats.fluxDissipation.modifyPercent("sc_together_as_one", mod)

        ship.mutableStats.ballisticWeaponDamageMult.modifyPercent("sc_together_as_one", mod)
        ship.mutableStats.energyWeaponDamageMult.modifyPercent("sc_together_as_one", mod)
        ship.mutableStats.missileWeaponDamageMult.modifyPercent("sc_together_as_one", mod)


        recentCount = count

    }
}